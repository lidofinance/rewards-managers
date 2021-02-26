import pytest
import brownie
from brownie.network.state import Chain

ZERO_ADDRESS = brownie.ZERO_ADDRESS
ONE_WEEK = 60 * 60 * 24 * 7
rewards_period = ONE_WEEK

def test_stranger_fails_to_transfer_ownership(rewards_manager, stranger):
    with brownie.reverts('not permitted'):
        rewards_manager.transfer_ownership(stranger, {'from': stranger})

def test_owner_transfers_ownership(rewards_manager, stranger, lido_rewards_manager_deployer):
    rewards_manager.transfer_ownership(stranger, {'from': lido_rewards_manager_deployer})
    assert rewards_manager.owner() == stranger

def test_stranger_fails_to_set_rewards_contract(rewards_manager, stranger, joint_campaign):
    with brownie.reverts('not permitted'):
        rewards_manager.set_rewards_contract(joint_campaign.address, {'from': stranger})

def test_owner_sets_rewards_contract(rewards_manager, stranger, lido_rewards_manager_deployer, joint_campaign):
    rewards_manager.set_rewards_contract(joint_campaign.address, {'from': lido_rewards_manager_deployer})
    assert rewards_manager.rewards_contract() == joint_campaign.address

def test_stranger_recovers_ldo_from_campaign(rewards_manager, stranger, joint_campaign, lido_rewards_manager_deployer, ldo_token, lido_dao_agent_address):
    AMOUNT = brownie.Wei('1 ether')
    ldo_token.transfer(joint_campaign.address, AMOUNT, {'from': lido_dao_agent_address})
    rewards_manager.set_rewards_contract(joint_campaign.address, {'from': lido_rewards_manager_deployer})
    rewards_manager.recover_ldo_from_campaign(AMOUNT, {'from': lido_rewards_manager_deployer})
    assert ldo_token.balanceOf(lido_rewards_manager_deployer) == AMOUNT

def test_stranger_checks_collab_rewards_period_finish(rewards_manager, stranger, joint_campaign, lido_rewards_manager_deployer):
    rewards_manager.set_rewards_contract(joint_campaign.address, {'from': lido_rewards_manager_deployer})
    assert rewards_manager.collab_rewards_period_finish({'from': stranger}) == 0

def test_stranger_fails_to_change_manager(rewards_manager, stranger, lido_rewards_manager_deployer, joint_campaign):
    rewards_manager.set_rewards_contract(joint_campaign.address, {'from': lido_rewards_manager_deployer})
    with brownie.reverts('not permitted'):
      rewards_manager.change_manager(stranger, {'from': stranger})

def test_owner_fails_to_change_manager_without_rewards_contract(rewards_manager, stranger, lido_rewards_manager_deployer, joint_campaign):
    with brownie.reverts('manager: no rewards contract'):
      rewards_manager.change_manager(stranger, {'from': lido_rewards_manager_deployer})

def test_owner_changes_manager(rewards_manager, stranger, lido_rewards_manager_deployer, joint_campaign):
    rewards_manager.set_rewards_contract(joint_campaign.address, {'from': lido_rewards_manager_deployer})
    rewards_manager.change_manager(stranger, {'from': lido_rewards_manager_deployer})
    assert joint_campaign.collabRewardsDistributor() == stranger

def test_stranger_recovers_erc20(ldo_token, stranger, rewards_manager, lido_rewards_manager_deployer, lido_dao_agent_address):
    AMOUNT = brownie.Wei('1 ether')
    balance_before = ldo_token.balanceOf(lido_rewards_manager_deployer)
    ldo_token.transfer(rewards_manager.address, AMOUNT, {'from': lido_dao_agent_address})
    rewards_manager.recover_erc20(ldo_token.address, AMOUNT, {'from': stranger})
    balance_after = ldo_token.balanceOf(lido_rewards_manager_deployer)
    assert balance_after - balance_before == AMOUNT

def test_can_not_start_rewards_without_rewards_contract(ldo_token, lido_dao_agent_address, rewards_manager, stranger):
    LDO_REWARD_AMOUNT = brownie.Wei('1 ether')
    ldo_token.transfer(rewards_manager.address, LDO_REWARD_AMOUNT, {'from': lido_dao_agent_address})
    with brownie.reverts():
        rewards_manager.start_next_rewards_period({'from': stranger})

def test_can_not_start_rewards_without_tokens(ldo_token, lido_dao_agent_address, rewards_manager, stranger, joint_campaign, lido_rewards_manager_deployer):
    rewards_manager.set_rewards_contract(joint_campaign.address, {'from': lido_rewards_manager_deployer})
    with brownie.reverts():
        rewards_manager.start_next_rewards_period({'from': stranger})

def test_can_not_start_rewards_before_current_finish(rewards_manager, lido_rewards_manager_deployer, lido_dao_agent_address, joint_campaign, ldo_token, arcx_deployer, stranger):
    chain = Chain()
    LDO_REWARD_AMOUNT = brownie.Wei('1 ether')
    REWARDS_DURATION = 24* 60 * 60
    rewards_manager.set_rewards_contract(joint_campaign.address, {'from': lido_rewards_manager_deployer})
    ldo_token.transfer(rewards_manager.address, LDO_REWARD_AMOUNT, {'from': lido_dao_agent_address})
    # Start reward period
    joint_campaign.setRewardsDuration(REWARDS_DURATION, {'from': arcx_deployer})

    rewards_manager.start_next_rewards_period({'from': stranger})

    with brownie.reverts():
      rewards_manager.start_next_rewards_period({'from': stranger})

    chain.sleep(REWARDS_DURATION + 1)
    chain.mine()

    assert rewards_manager.is_rewards_period_finished()

    ldo_token.transfer(rewards_manager.address, LDO_REWARD_AMOUNT, {'from': lido_dao_agent_address})
    rewards_manager.start_next_rewards_period({'from': stranger})

    assert not rewards_manager.is_rewards_period_finished()
