from brownie import Wei, chain
from scripts.deploy import deploy_manager
from utils.config import (
    gift_index,
    one_inch_token_owner,
    farming_rewards_owner,
    farming_rewards_address,
    mooniswap_address,
    initial_rewards_duration_sec,
    rewards_amount,
)

# Test Case:
# 1. Deploy and configure rewards manager
# 2. Reward farming contract sets reward manager as distributor for LDO token gift
# 3. DAO transfers LDO to reward manager contract
# 4. 1INCH distributor transfers tokens to farming contract directly
# 5. Someone starts new reward period (1INCH via their distributor, LDO via reward manager)
# 6. Users A and B are obtaining stETH and DAI tokens somehow
# 7. Users A and B deposit their stETH and DAI tokens to liquidity pool to receive LP tokens
# 8. Users A and B are staking their LP tokens to reward farming contract
# 9. User A exists from reward farming contract after half of rewarding period
# 10. User A withdraws tokens from liquidity pool
# 11. User B exists from reward farming contract after full rewarding period
# 12. User B withdraws tokens from liquidity pool
# 13. User B has more rewards than A
# ------- SECOND PERIOD -------
# 14. DAO transfers LDO to reward manager contract
# 15. 1INCH distributor transfers tokens to farming contract directly
# 16. Someone starts new reward period (1INCH via their distributor, LDO via reward manager)
# 17. Users A deposits some stETH and DAI tokens to liquidity pool to receive LP tokens
# 18. Users A stakes LP tokens to reward farming contract
# 19. User A exists from reward farming contract after an end of rewarding period
# 20. User A withdraws tokens from liquidity pool
def test_happy_path(
    interface,
    accounts,
    ape,
    stranger,
    ldo_token,
    steth_token,
    dai_token,
    one_inch_token,
    dao_voting_impersonated,
    dao_agent
):
    rewards_period = initial_rewards_duration_sec
    dai_holder = "0xa405445ff6ed916b820a744621ef473b260b0c1c"

    mooniswap = interface.Mooniswap(mooniswap_address)
    farming_rewards = interface.FarmingRewards(farming_rewards_address)

    # Deploy and configure rewards manager
    rewards_manager = deploy_manager({"from": ape}, publish_source=False)

    # Reward farming contract sets reward manager as distributor for LDO token gift
    farming_rewards.setRewardDistribution(gift_index, rewards_manager, {"from": farming_rewards_owner})

    # DAO transfers LDO tokens to reward manager
    assert ldo_token.balanceOf(dao_agent) >= rewards_amount

    transfer_calldata = ldo_token.transfer.encode_input(rewards_manager, rewards_amount)

    dao_agent.execute(
        ldo_token, 0, transfer_calldata, {"from": dao_voting_impersonated}
    )

    assert ldo_token.balanceOf(rewards_manager) == rewards_amount

    # 1INCH distributor transfers tokens to farming contract directly
    one_inch_token.transfer(farming_rewards, rewards_amount, {"from": one_inch_token_owner})

    assert one_inch_token.balanceOf(farming_rewards) == rewards_amount

    # Someone starts new reward period
    # 1INCH via their distributor
    farming_rewards.notifyRewardAmount(0, rewards_amount, {"from": farming_rewards_owner})

    # LDO via reward manager
    rewards_manager.start_next_rewards_period({"from": stranger})

    assert ldo_token.balanceOf(rewards_manager) == 0
    assert ldo_token.balanceOf(farming_rewards) == rewards_amount

    assert rewards_manager.is_rewards_period_finished() == False

    # Users A and B are obtaining stETH and DAI tokens somehow
    user_a, user_b = accounts[2], accounts[3]

    user_a.transfer(steth_token, Wei("3 ether"))
    user_b.transfer(steth_token, Wei("3 ether"))

    assert steth_token.balanceOf(user_a) > 0
    assert steth_token.balanceOf(user_b) > 0

    dai_token.transfer(user_a, Wei("3 ether"), {"from": dai_holder})
    dai_token.transfer(user_b, Wei("3 ether"), {"from": dai_holder})

    assert dai_token.balanceOf(user_a) > 0
    assert dai_token.balanceOf(user_b) > 0

    # Users A and B deposit their stETH and DAI tokens to liquidity pool to receive LP tokens
    steth_token.approve(mooniswap, 1500, {"from": user_a})
    dai_token.approve(mooniswap, 1500, {"from": user_a})

    steth_token.approve(mooniswap, 2000, {"from": user_b})
    dai_token.approve(mooniswap, 2000, {"from": user_b})

    mooniswap.deposit([1500, 1500], [1000, 1000], {"from": user_a})
    mooniswap.deposit([2000, 2000], [1500, 1500], {"from": user_b})

    user_a_balance_lp = mooniswap.balanceOf(user_a)
    user_b_balance_lp = mooniswap.balanceOf(user_b)

    assert user_a_balance_lp > 0
    assert user_b_balance_lp > 0

    mooniswap.approve(farming_rewards, user_a_balance_lp, {"from": user_a})
    mooniswap.approve(farming_rewards, user_b_balance_lp, {"from": user_b})

    # Users A and B are staking their LP tokens to reward farming contract
    farming_rewards.stake(user_a_balance_lp, {"from": user_a})
    farming_rewards.stake(user_b_balance_lp, {"from": user_b})

    assert farming_rewards.balanceOf(user_a) > 0
    assert farming_rewards.balanceOf(user_b) > 0

    # User A exists from reward farming contract after half of rewarding period
    chain.sleep(rewards_period // 2)
    chain.mine()

    assert rewards_manager.is_rewards_period_finished() == False

    farming_rewards.exit({"from": user_a})

    user_a_one_inch_balance_before = one_inch_token.balanceOf(user_a)
    user_a_ldo_balance_before = ldo_token.balanceOf(user_a)

    assert user_a_one_inch_balance_before > 0
    assert user_a_ldo_balance_before > 0
    assert mooniswap.balanceOf(user_a) > 0

    # User A withdraws tokens from liquidity pool
    user_a_dai_balance_before = dai_token.balanceOf(user_a)
    user_a_steth_balance_before = steth_token.balanceOf(user_a)

    mooniswap.withdraw(mooniswap.balanceOf(user_a), [1000, 1000], {"from": user_a})

    user_a_one_inch_balance_after = one_inch_token.balanceOf(user_a)
    user_a_ldo_balance_after = ldo_token.balanceOf(user_a)
    user_a_dai_balance_after = dai_token.balanceOf(user_a)
    user_a_steth_balance_after = steth_token.balanceOf(user_a)

    assert user_a_one_inch_balance_after == user_a_one_inch_balance_before
    assert user_a_ldo_balance_after == user_a_ldo_balance_before
    assert user_a_dai_balance_after > user_a_dai_balance_before
    assert user_a_steth_balance_after > user_a_steth_balance_before

    # User B exists from reward farming contract after full rewarding period
    chain.sleep(rewards_period)
    chain.mine()

    assert rewards_manager.is_rewards_period_finished() == True

    farming_rewards.exit({"from": user_b})

    user_b_one_inch_balance_before = one_inch_token.balanceOf(user_b)
    user_b_ldo_balance_before = ldo_token.balanceOf(user_b)

    assert user_b_one_inch_balance_before > 0
    assert user_b_ldo_balance_before > 0
    assert mooniswap.balanceOf(user_b) > 0

    # User B withdraws tokens from liquidity pool
    user_b_dai_balance_before = dai_token.balanceOf(user_b)
    user_b_steth_balance_before = steth_token.balanceOf(user_b)

    mooniswap.withdraw(mooniswap.balanceOf(user_b), [1500, 1500], {"from": user_b})

    user_b_one_inch_balance_after = one_inch_token.balanceOf(user_b)
    user_b_ldo_balance_after = ldo_token.balanceOf(user_b)
    user_b_dai_balance_after = dai_token.balanceOf(user_b)
    user_b_steth_balance_after = steth_token.balanceOf(user_b)

    assert user_b_one_inch_balance_after == user_b_one_inch_balance_before
    assert user_b_ldo_balance_after == user_b_ldo_balance_before
    assert user_b_dai_balance_after > user_b_dai_balance_before
    assert user_b_steth_balance_after > user_b_steth_balance_before

    # User B has more rewards than A
    assert user_a_ldo_balance_after < user_b_ldo_balance_after
    assert user_a_one_inch_balance_after < user_b_one_inch_balance_after

    # ------------------------------
    # SECOND ITERATION
    # ------------------------------

    # DAO transfers LDO tokens to reward manager
    assert ldo_token.balanceOf(dao_agent) >= rewards_amount

    transfer_calldata = ldo_token.transfer.encode_input(rewards_manager, rewards_amount)

    dao_agent.execute(
        ldo_token, 0, transfer_calldata, {"from": dao_voting_impersonated}
    )

    assert ldo_token.balanceOf(rewards_manager) == rewards_amount

    # 1INCH distributor transfers tokens to farming contract directly
    one_inch_token.transfer(farming_rewards, rewards_amount, {"from": one_inch_token_owner})

    assert one_inch_token.balanceOf(farming_rewards) >= rewards_amount

    # Someone starts new reward period
    # 1INCH via their distributor
    farming_rewards.notifyRewardAmount(0, rewards_amount, {"from": farming_rewards_owner})

    # Some tokens may be left after previous rewarding period
    fr_ldo_balance_before = ldo_token.balanceOf(farming_rewards)

    # LDO via reward manager
    rewards_manager.start_next_rewards_period({"from": stranger})

    fr_ldo_balance_after = ldo_token.balanceOf(farming_rewards)

    assert ldo_token.balanceOf(rewards_manager) == 0
    assert fr_ldo_balance_after == fr_ldo_balance_before + rewards_amount

    # Users A deposits some stETH and DAI tokens to liquidity pool to receive LP tokens
    assert rewards_manager.is_rewards_period_finished() == False

    steth_token.approve(mooniswap, 1000, {"from": user_a})
    dai_token.approve(mooniswap, 1000, {"from": user_a})

    mooniswap.deposit([1000, 1000], [500, 500], {"from": user_a})

    user_a_balance_lp = mooniswap.balanceOf(user_a)

    mooniswap.approve(farming_rewards, user_a_balance_lp, {"from": user_a})

    # Users A stakes LP tokens to reward farming contract
    farming_rewards.stake(user_a_balance_lp, {"from": user_a})

    # User A exists from reward farming contract after an end of rewarding period
    chain.sleep(rewards_period)
    chain.mine()

    assert rewards_manager.is_rewards_period_finished() == True

    farming_rewards.exit({"from": user_a})

    # User A withdraws tokens from liquidity pool
    mooniswap.withdraw(mooniswap.balanceOf(user_a), [750, 750], {"from": user_a})
