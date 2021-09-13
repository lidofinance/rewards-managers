from brownie import Wei, StakingRewardsSushi, RewardsManager
from brownie.network.state import Chain

ONE_WEEK = 60 * 60 * 24 * 7

# Test Case:
# 1. Deploy Rewarder and add to MasterChefV2 pool with deployed rewarder
# 2. Deploy RewardManager and connect it to Rewarder
# 3. DAO transfers LDO to RewardsManager contract
# 4. Someone starts new reward period
# 5. Users A and B buy wstETH tokens and exchange ETH on DAI to become lp providers
# 6. Users A and B deposit their lp tokens into the created pool via MasterChefV2 contract
# 7. Wait half of the reward period and harvest rewards by test users
# 8. Harvest reward again when reward period passed
# 9. DAO transfers LDO to RewardsManager contract to start second reward period
# 10. Stranger starts new reward period
# 11. User A withdraws money and harvest at the middle of second reward period
# 12. Wait till the end of the second reward period
# 13. User B harvest money for passed period
# 14. User A has no rewards because he withdrawn his tokens earlier
def test_happy_path(
    accounts,
    ldo_token,
    dao_voting_impersonated,
    dao_agent,
    ape,
    stranger,
    lp_token_sushi,
    master_chef_v2,
    master_chef_v2_owner,
    sushiswap_router,
    wsteth_token,
    dai_token,
):
    chain = Chain()
    rewards_period = ONE_WEEK
    reward_amount = Wei("1 ether")

    # deploy rewards manager
    rewards_manager = RewardsManager.deploy({"from": ape})

    # deploy rewarder contract
    staking_rewards_sushi = StakingRewardsSushi.deploy(
        ape,
        rewards_manager,
        ldo_token,
        lp_token_sushi,
        rewards_period,
        {"from": ape},
    )

    # create pool in MasterChefV2 with deployed rewarder
    master_chef_v2.add(
        100, lp_token_sushi, staking_rewards_sushi, {"from": master_chef_v2_owner}
    )
    pid = master_chef_v2.poolLength() - 1

    # set rewards contract in RewardsManager
    rewards_manager.set_rewards_contract(staking_rewards_sushi, {"from": ape})

    # DAO transfers the rewards to the contract to spend LDO
    assert ldo_token.balanceOf(dao_agent) >= reward_amount
    transfer_calldata = ldo_token.transfer.encode_input(rewards_manager, reward_amount)
    dao_agent.execute(
        ldo_token, 0, transfer_calldata, {"from": dao_voting_impersonated}
    )
    assert ldo_token.balanceOf(rewards_manager) == reward_amount

    # someone starts the first rewards period
    rewards_manager.start_next_rewards_period({"from": stranger})
    assert rewards_manager.is_rewards_period_finished() == False

    user_a, user_b = accounts[2], accounts[3]

    # user A adds liquidity to the pool to gain lpTokens:
    # transfer ETH to wstETH token to receive wstETH
    user_a.transfer(wsteth_token, "3 ether")

    # Exchange ETH to DAI token to receive DAI
    sushiswap_router.swapExactETHForTokens(
        Wei("100 ether"),
        [
            "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
            "0x6b175474e89094c44da98b954eedeac495271d0f",
        ],  # weth9
        user_a,
        10000000000,
        {"from": user_a, "value": Wei("3 ether")},
    )
    wsteth_token.approve(sushiswap_router, Wei("100 ether"), {"from": user_a})
    dai_token.approve(sushiswap_router, Wei("10000 ether"), {"from": user_a})

    sushiswap_router.addLiquidity(
        wsteth_token,
        dai_token,
        Wei("1 ether"),
        Wei("3000 ether"),
        Wei("0.9 ether"),
        Wei("2900 ether"),
        user_a,
        10000000000,
        {"from": user_a},
    )
    user_a_stake = lp_token_sushi.balanceOf(user_a)

    # user B adds liquidity to the pool to gain lpTokens:

    # transfer ETH to wstETH token to receive wstETH
    user_b.transfer(wsteth_token, "3 ether")

    # Exchange ETH to DAI token to receive DAI
    sushiswap_router.swapExactETHForTokens(
        Wei("100 ether"),
        [
            "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
            "0x6b175474e89094c44da98b954eedeac495271d0f",
        ],  # weth9
        user_b,
        10000000000,
        {"from": user_b, "value": Wei("3 ether")},
    )
    wsteth_token.approve(sushiswap_router, Wei("100 ether"), {"from": user_b})
    dai_token.approve(sushiswap_router, Wei("10000 ether"), {"from": user_b})

    sushiswap_router.addLiquidity(
        wsteth_token,
        dai_token,
        Wei("2 ether"),
        Wei("6000 ether"),
        Wei("1.9 ether"),
        Wei("5900 ether"),
        user_b,
        10000000000,
        {"from": user_b},
    )
    user_b_stake = lp_token_sushi.balanceOf(user_b)

    # Deposit tokens to the pool
    lp_token_sushi.approve(master_chef_v2, user_a_stake, {"from": user_a})
    master_chef_v2.deposit(pid, user_a_stake, user_a, {"from": user_a})

    lp_token_sushi.approve(master_chef_v2, user_b_stake, {"from": user_b})
    master_chef_v2.deposit(pid, user_b_stake, user_b, {"from": user_b})

    assert staking_rewards_sushi.balanceOf(user_a) == user_a_stake
    assert staking_rewards_sushi.balanceOf(user_b) == user_b_stake

    # wait half of the reward period
    chain.sleep(rewards_period // 2)
    chain.mine()

    # harvest rewards
    user_a_earned = [staking_rewards_sushi.earned(user_a)]
    master_chef_v2.harvest(pid, user_a, {"from": user_a})
    user_b_earned = [staking_rewards_sushi.earned(user_b)]
    master_chef_v2.harvest(pid, user_b, {"from": user_b})

    # half of rewards must be distributed
    expected_total_reward = reward_amount // 2
    exptexted_user_a_reward = (
        expected_total_reward * user_a_stake // (user_a_stake + user_b_stake)
    )
    exptexted_user_b_reward = (
        expected_total_reward * user_b_stake // (user_a_stake + user_b_stake)
    )

    # validate correct rewards were paid
    # allow payment mismatch equal to the payment for 5 secs
    payment_epsilon = 5 * staking_rewards_sushi.rewardRate()
    assert abs(exptexted_user_a_reward - user_a_earned[0]) < payment_epsilon
    assert abs(exptexted_user_b_reward - user_b_earned[0]) < payment_epsilon

    assert abs(ldo_token.balanceOf(user_a) - user_a_earned[0]) < payment_epsilon
    assert abs(ldo_token.balanceOf(user_b) - user_b_earned[0]) < payment_epsilon

    # wait while the reward period will pass completely
    assert rewards_manager.is_rewards_period_finished() == False
    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.is_rewards_period_finished() == True

    # harvest rewards again
    user_a_earned.append(staking_rewards_sushi.earned(user_a))
    master_chef_v2.harvest(pid, user_a, {"from": user_a})
    user_b_earned.append(staking_rewards_sushi.earned(user_b))
    master_chef_v2.harvest(pid, user_b, {"from": user_b})

    # validate correct rewards were paid
    assert abs(ldo_token.balanceOf(user_a) - sum(user_a_earned)) < payment_epsilon
    assert abs(ldo_token.balanceOf(user_b) - sum(user_b_earned)) < payment_epsilon

    # DAO transfers the rewards to the contract to start second reward period
    reward_amount = Wei("0.5 ether")
    assert ldo_token.balanceOf(dao_agent) >= reward_amount
    transfer_calldata = ldo_token.transfer.encode_input(rewards_manager, reward_amount)
    dao_agent.execute(
        ldo_token, 0, transfer_calldata, {"from": dao_voting_impersonated}
    )
    assert ldo_token.balanceOf(rewards_manager) == reward_amount

    # someone starts the second rewards period
    rewards_manager.start_next_rewards_period({"from": stranger})
    assert rewards_manager.is_rewards_period_finished() == False

    # wait half of the reward period
    chain.sleep(rewards_period // 2)
    chain.mine()

    # user A decides to withdraw money from pool
    user_a_earned.append(staking_rewards_sushi.earned(user_a))
    master_chef_v2.withdraw(pid, user_a_stake, user_a, {"from": user_a})

    # validate that user has no lp tokens after withdraw and correct reward was paid
    assert staking_rewards_sushi.balanceOf(user_a) == 0
    assert abs(ldo_token.balanceOf(user_a) - sum(user_a_earned)) < payment_epsilon

    # wait while the second reward period will pass completely
    assert rewards_manager.is_rewards_period_finished() == False
    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.is_rewards_period_finished() == True

    # user B harvest rewards
    user_b_earned.append(staking_rewards_sushi.earned(user_b))
    master_chef_v2.harvest(pid, user_b, {"from": user_b})
    assert abs(ldo_token.balanceOf(user_b) - sum(user_b_earned)) < payment_epsilon

    # when user A harvest rewards he has to receive nothing because
    # he has already withdrawn his lpTokens from pool
    user_a_earned.append(staking_rewards_sushi.earned(user_a))
    master_chef_v2.harvest(pid, user_a, {"from": user_a})
    assert abs(ldo_token.balanceOf(user_a) - sum(user_a_earned[:4])) < payment_epsilon
    assert user_a_earned[-1] == 0
