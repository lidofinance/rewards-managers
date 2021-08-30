from brownie import (
    Wei,
    chain,
    ZERO_ADDRESS,
    RewardsManager,
    Mooniswap,
    MooniswapFactoryGovernance,
    FarmingRewards,
);

from utils.config import (
    one_inch_token_owner,
    initial_rewards_duration_sec,
    rewards_amount,
    scale
)

# Test Case:
# 0. Deploy dependency contracts (should be removed when they will be available on-chain)
# 1. Deploy and configure rewards manager
# 2. Reward farming contract adds LDO token as gift with reward manager as distributor
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
def test_happy_path(
    accounts,
    ape,
    stranger,
    ldo_token,
    steth_token,
    dai_token,
    one_inch_token,
    dao_voting_impersonated,
    dao_agent,
):
    rewards_period = initial_rewards_duration_sec
    dai_holder = "0xa405445ff6ed916b820a744621ef473b260b0c1c"

    # Deploy dependency contracts (should be removed when they will be available on-chain)
    mooniswap_factory = MooniswapFactoryGovernance.deploy(ZERO_ADDRESS, {"from": stranger})
    mooniswap = Mooniswap.deploy(steth_token, dai_token, "stETH-DAI Liquidity Pool Token", "LP", mooniswap_factory, {"from": stranger})
    farming_rewards = FarmingRewards.deploy(mooniswap, one_inch_token, rewards_period, stranger, scale, {"from": stranger})

    # Deploy and configure rewards manager
    rewards_manager = RewardsManager.deploy({"from": ape})

    rewards_manager.set_rewards_contract(farming_rewards, {"from": ape})
    rewards_manager.set_gift_index(1, {"from": ape})

    # Reward farming contract adds LDO token as gift with reward manager as distributor
    farming_rewards.addGift(ldo_token, rewards_period, rewards_manager, scale, {"from": stranger})

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
    farming_rewards.notifyRewardAmount(0, rewards_amount, {"from": stranger})

    # LDO via reward manager
    rewards_manager.start_next_rewards_period({"from": stranger})

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
