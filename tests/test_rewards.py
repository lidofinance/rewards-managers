import pytest
import brownie

ZERO_ADDRESS = brownie.ZERO_ADDRESS
ONE_WEEK = 60 * 60 * 24 * 7
rewards_period = ONE_WEEK

def test_stranger_fails_to_set_rewards_contract_in_reward_distributor(rewards_manager, stranger, joint_campaign):
  with brownie.reverts():
    rewards_manager.set_rewards_contract(joint_campaign.address, {'from': stranger})

def test_reward_distributor_is_set_up(rewards_manager, lido_rewards_manager_deployer, joint_campaign):
  rewards_manager.set_rewards_contract(joint_campaign.address, {'from': lido_rewards_manager_deployer})
  assert rewards_manager.rewards_contract()  == joint_campaign.address

def test_reward_distributor_starts_next_rewards_period(stranger, rewards_manager, lido_rewards_manager_deployer, joint_campaign, lido_dao_agent_address, ldo_token, arcx_deployer):
  AMOUNT = brownie.Wei('100000 ether')
  ldo_token.transfer(rewards_manager, AMOUNT,{'from': lido_dao_agent_address})
  rewards_manager.set_rewards_contract(joint_campaign.address, {'from': lido_rewards_manager_deployer})
  assert rewards_manager.is_rewards_period_finished()
  assert joint_campaign.collabRewardsDistributor() == rewards_manager.address
  assert joint_campaign.collabRewardToken() == ldo_token.address
  assert joint_campaign.isInitialized()
  joint_campaign.setRewardsDuration(60*60*24, {'from': arcx_deployer})
  assert joint_campaign.rewardsDuration() == 60*60*24

  tx = rewards_manager.start_next_rewards_period({'from': lido_rewards_manager_deployer})

  assert tx.events['RewardAdded']['_reward'] == AMOUNT
  assert tx.events['RewardAdded']['_rewardToken'] == ldo_token.address

def test_reward_manager_recovers_collab(joint_campaign, rewards_manager, ldo_token, lido_dao_agent_address, lido_rewards_manager_deployer):
  AMOUNT = brownie.Wei('1 ether')
  ldo_token.transfer(joint_campaign, AMOUNT,{'from': lido_dao_agent_address})
  rewards_manager.set_rewards_contract(joint_campaign.address, {'from': lido_rewards_manager_deployer})
  assert joint_campaign.rewardsDuration() == 0
  assert ldo_token.balanceOf(joint_campaign) >= AMOUNT
  assert joint_campaign.collabRewardsDistributor() == rewards_manager.address
  assert rewards_manager.owner() == lido_rewards_manager_deployer
  assert rewards_manager.rewards_contract() == joint_campaign.address

  rewards_manager_deployer_ldo_balance_before = ldo_token.balanceOf(lido_rewards_manager_deployer)

  rewards_manager.recover_ldo_from_campaign(AMOUNT, {'from': lido_rewards_manager_deployer})

  rewards_manager_deployer_ldo_balance_after = ldo_token.balanceOf(lido_rewards_manager_deployer)
  assert rewards_manager_deployer_ldo_balance_after - rewards_manager_deployer_ldo_balance_before == AMOUNT

def test_reward_manager_changes_manager_in_campaign(lido_rewards_manager_deployer, rewards_manager, joint_campaign, stranger):

  rewards_manager.set_rewards_contract(joint_campaign.address, {'from': lido_rewards_manager_deployer})
  assert joint_campaign.collabRewardsDistributor() == rewards_manager.address

  rewards_manager.change_manager(stranger, {'from': lido_rewards_manager_deployer})

  assert joint_campaign.collabRewardsDistributor() == stranger

def test_manager_recovers_erc20_and_eth(ldo_token, stranger, rewards_manager, lido_rewards_manager_deployer, lido_dao_agent_address):
    AMOUNT = brownie.Wei('1 ether')
    stranger.transfer(rewards_manager, AMOUNT)

    balance_before = lido_rewards_manager_deployer.balance()

    rewards_manager.recover_erc20(ldo_token.address, AMOUNT, {'from': stranger})
    balance_after = lido_rewards_manager_deployer.balance()
    assert balance_after - balance_before == AMOUNT
