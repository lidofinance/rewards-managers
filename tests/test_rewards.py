from brownie import Wei, StakingRewardsSushi, RewardsManager
from brownie.network.state import Chain

ONE_WEEK = 60 * 60 * 24 * 7


def test_happy_path(
    steth_token,
    lp_token,
    steth_pool,
    gauge,
    gauge_admin,
    ldo_token,
    dao_voting_impersonated,
    dao_agent,
    ape,
    stranger,
    steth_whale,
    curve_farmer,
    rewards_helpers,
):
    chain = Chain()

    # deploying and installing the rewards contract

    rewards_period = ONE_WEEK
    reward_amount = Wei("1 ether")

    (rewards_manager, rewards_contract) = rewards_helpers.deploy_rewards(
        rewards_period=rewards_period, deployer=ape
    )

    rewards_helpers.install_rewards(
        gauge=gauge,
        gauge_admin=gauge_admin,
        rewards_token=ldo_token,
        rewards=rewards_contract,
    )

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

    # the whale provides liquidity and locks their LP tokens into the gauge

    steth_deposit_amount = steth_token.balanceOf(steth_whale)
    assert steth_deposit_amount > 0

    steth_token.approve(steth_pool, steth_deposit_amount, {"from": steth_whale})
    steth_pool.add_liquidity([0, steth_deposit_amount], 0, {"from": steth_whale})

    lp_token_deposit_amount = lp_token.balanceOf(steth_whale)
    assert lp_token_deposit_amount > 0
    assert steth_token.balanceOf(steth_whale) <= 1

    lp_token.approve(gauge, lp_token_deposit_amount, {"from": steth_whale})
    gauge.deposit(lp_token_deposit_amount, {"from": steth_whale})

    assert lp_token.balanceOf(steth_whale) == 0
    assert gauge.balanceOf(steth_whale) > 0

    # the farmer already has their LP tokens locked into the gauge

    assert gauge.balanceOf(curve_farmer) > 0

    whale_ldo_prev_balance = ldo_token.balanceOf(steth_whale)
    farmer_ldo_prev_balance = ldo_token.balanceOf(curve_farmer)

    assert whale_ldo_prev_balance == 0

    # rewards period partially passes; folks claim their rewards

    chain.sleep(rewards_period // 2)
    gauge.claim_rewards({"from": steth_whale})
    gauge.claim_rewards({"from": curve_farmer})

    whale_ldo_balance = ldo_token.balanceOf(steth_whale)
    farmer_ldo_balance = ldo_token.balanceOf(curve_farmer)

    assert whale_ldo_balance > 0
    assert farmer_ldo_balance > farmer_ldo_prev_balance
    whale_ldo_prev_balance, farmer_ldo_prev_balance = (
        whale_ldo_balance,
        farmer_ldo_balance,
    )

    # rewards period fully passes; folks claim their rewards once again

    assert rewards_manager.is_rewards_period_finished() == False
    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.is_rewards_period_finished() == True

    gauge.claim_rewards({"from": steth_whale})
    gauge.claim_rewards({"from": curve_farmer})

    whale_ldo_balance = ldo_token.balanceOf(steth_whale)
    farmer_ldo_balance = ldo_token.balanceOf(curve_farmer)

    assert whale_ldo_balance > whale_ldo_prev_balance
    assert farmer_ldo_balance > farmer_ldo_prev_balance

    whale_ldo_prev_balance = ldo_token.balanceOf(steth_whale)
    farmer_ldo_prev_balance = ldo_token.balanceOf(curve_farmer)

    # DAO transfers the rewards to the contract once again

    assert ldo_token.balanceOf(dao_agent) >= reward_amount
    transfer_calldata = ldo_token.transfer.encode_input(rewards_manager, reward_amount)
    dao_agent.execute(
        ldo_token, 0, transfer_calldata, {"from": dao_voting_impersonated}
    )
    assert ldo_token.balanceOf(rewards_manager) == reward_amount

    # someone starts the second rewards period

    rewards_manager.start_next_rewards_period({"from": stranger})
    assert rewards_manager.is_rewards_period_finished() == False

    # rewards period partially passes

    chain.sleep(rewards_period // 2)
    chain.mine()

    assert rewards_manager.is_rewards_period_finished() == False

    # farmer wants to get out because it's not over 9000 apy anymore

    gauge.withdraw(gauge.balanceOf(curve_farmer), {"from": curve_farmer})

    farmer_ldo_balance = ldo_token.balanceOf(curve_farmer)
    assert farmer_ldo_balance > farmer_ldo_prev_balance
    assert gauge.balanceOf(curve_farmer) == 0

    farmer_ldo_prev_balance = ldo_token.balanceOf(curve_farmer)

    # rewards period fully passes

    chain.sleep(rewards_period // 2 + 100)
    chain.mine()

    assert rewards_manager.is_rewards_period_finished() == True

    # whale still claim their rewards

    gauge.claim_rewards({"from": steth_whale})
    whale_ldo_balance = ldo_token.balanceOf(steth_whale)
    assert whale_ldo_balance > whale_ldo_prev_balance

    # farmer gets no reward cause she's out

    gauge.claim_rewards({"from": curve_farmer})
    farmer_ldo_balance = ldo_token.balanceOf(curve_farmer)
    assert farmer_ldo_balance == farmer_ldo_prev_balance
    assert gauge.balanceOf(curve_farmer) == 0


# Test Case:
# 1. Deploy Rewarder and add to MasterChefV2 pool with deployed rewarder
# 2. Deploy RewardManager and connect it to Rewarder
# 3. DAO transfers LDO to RewardsManager contract
# 4. Someone starts new reward period
# 5. Transfer lpTokens to test users A and B
# 5. Users A and B deposit their lp tokens into the created pool via MasterChefV2 contract
# 6. Wait half of the reward period and harvest rewards by test users
# 7. Harvest reward again when reward period passed
# 8. DAO transfers LDO to RewardsManager contract to start second reward period
# 9. Stranger starts new reward period
# 10. User A withdraws money and harvest at the middle of second reward period
# 11. Wait till the end of the second reward period
# 12. User B harvest money for passed period
# 13. User A has no rewards because he withdrawn his tokens earlier
def test_happy_path_sushi(
    accounts,
    ldo_token,
    dao_voting_impersonated,
    dao_agent,
    ape,
    stranger,
    lp_token_sushi,
    master_chef_v2,
    master_chef_v2_owner,
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
        master_chef_v2,
        {"from": ape},
    )
    print(rewards_manager, staking_rewards_sushi.rewardsDistribution())

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

    # Transfer lpTokens to test users
    user_a, user_b = accounts[2], accounts[3]
    user_a_stake, user_b_stake = 1000 * 10 ** 18, 2000 * 10 ** 18

    lp_token_sushi.transfer(user_a, user_a_stake, {"from": ape})
    lp_token_sushi.transfer(user_b, user_b_stake, {"from": ape})

    assert lp_token_sushi.balanceOf(user_a) == user_a_stake
    assert lp_token_sushi.balanceOf(user_b) == user_b_stake

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
