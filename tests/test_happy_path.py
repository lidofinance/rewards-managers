from brownie import Wei
from brownie.network.state import Chain

def test_happy_path(
    rewards_manager,
    lido_rewards_manager_deployer,
    ldo_token,
    lido_dao_agent_address,
    joint_campaign,
    arcx_deployer,
    staking_token_whale,
    staking_token,
    stranger
):
    chain = Chain()
    LDO_REWARD_AMOUNT = Wei('100000 ether')
    REWARDS_DURATION = 30 * 24 * 60 * 60

    # Set up joint campaign + rewards properly, check
    rewards_manager.set_rewards_contract(joint_campaign.address, {'from': lido_rewards_manager_deployer})

    assert joint_campaign.collabRewardsDistributor() == rewards_manager.address
    assert rewards_manager.rewards_contract() == joint_campaign.address
    assert ldo_token.balanceOf(joint_campaign.address) == 0
    assert ldo_token.balanceOf(rewards_manager.address) == 0

    # Transfer ldos from dao to manager
    ldo_token.transfer(rewards_manager.address, LDO_REWARD_AMOUNT, {'from': lido_dao_agent_address})
    assert ldo_token.balanceOf(rewards_manager.address) == LDO_REWARD_AMOUNT

    # Stake smth
    STAKE_AMOUNT = Wei('10 ether')
    staking_token.approve(joint_campaign.address, STAKE_AMOUNT, {'from': staking_token_whale})
    joint_campaign.stake(STAKE_AMOUNT, 1, {'from': staking_token_whale})
    assert ldo_token.balanceOf(staking_token_whale) == 0

    # Start reward period
    joint_campaign.setRewardsDuration(REWARDS_DURATION, {'from': arcx_deployer})

    # Call notify rewards
    rewards_manager.start_next_rewards_period({'from': stranger})
    assert ldo_token.balanceOf(joint_campaign.address) == LDO_REWARD_AMOUNT
    assert ldo_token.balanceOf(rewards_manager.address) == 0


    # Pass half a period, withdraw rewards

    chain.sleep(REWARDS_DURATION // 2)
    chain.mine()
    joint_campaign.getReward(staking_token_whale, {'from': stranger})
    assert ldo_token.balanceOf(staking_token_whale) > 0
    assert ldo_token.balanceOf(joint_campaign.address) > 0

    # Pass the whole period, withdraw rewards

    chain.sleep(REWARDS_DURATION // 2)
    chain.mine()
    joint_campaign.getReward(staking_token_whale, {'from': stranger})
    assert rewards_manager.is_rewards_period_finished()
    assert ldo_token.balanceOf(joint_campaign.address) + ldo_token.balanceOf(staking_token_whale) == LDO_REWARD_AMOUNT

    # Check there's only dust ldo left on the campaign
    assert ldo_token.balanceOf(joint_campaign.address) < Wei('1 ether')

    # Transfer ldos from dao agent to manager
    assert ldo_token.balanceOf(rewards_manager.address) == 0

    ldo_token.transfer(rewards_manager.address, LDO_REWARD_AMOUNT, {'from': lido_dao_agent_address})
    assert ldo_token.balanceOf(rewards_manager.address) == LDO_REWARD_AMOUNT

    # Notify rewards, check
    rewards_manager.start_next_rewards_period({'from': stranger})
    assert ldo_token.balanceOf(joint_campaign.address) > LDO_REWARD_AMOUNT
    assert ldo_token.balanceOf(rewards_manager.address) == 0

    assert not rewards_manager.is_rewards_period_finished()
