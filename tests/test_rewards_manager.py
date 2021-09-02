from brownie import reverts, ZERO_ADDRESS, chain, accounts, RewardsManager
from utils.config import (
    rewards_amount,
    gift_index,
    initial_rewards_duration_sec,
)


def test_owner_is_deployer(rewards_manager, farming_rewards, ape):
    assert rewards_manager.owner() == ape
    assert len(rewards_manager.tx.events) == 2
    assert rewards_manager.tx.events['RewardsContractSet']['rewards_contract'] == farming_rewards
    assert rewards_manager.tx.events['OwnershipTransferred']['previous_owner'] == ZERO_ADDRESS
    assert rewards_manager.tx.events['OwnershipTransferred']['new_owner'] == ape


def test_rewards_contract_address_is_not_zero(ape):
    with reverts("zero address"):
        RewardsManager.deploy(ZERO_ADDRESS, {"from": ape})


def test_stranger_cannot_transfer_ownership(rewards_manager, stranger):
    with reverts("not permitted"):
        rewards_manager.transfer_ownership(stranger, {"from": stranger})


def test_ownership_can_be_transferred(rewards_manager, ape, stranger):
    tx = rewards_manager.transfer_ownership(stranger, {"from": ape})

    assert rewards_manager.owner() == stranger
    assert len(tx.events) == 1
    assert tx.events['OwnershipTransferred']['previous_owner'] == ape
    assert tx.events['OwnershipTransferred']['new_owner'] == stranger


def test_ownership_can_be_transferred_to_zero_address(rewards_manager, ape):
    rewards_manager.transfer_ownership(ZERO_ADDRESS, {"from": ape})

    assert rewards_manager.owner() == ZERO_ADDRESS


def test_stranger_can_check_is_rewards_period_finished(rewards_manager, stranger):
    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == True


def test_period_finish(rewards_manager, farming_rewards):
    assert farming_rewards.tokenRewards(gift_index)[4] == rewards_manager.period_finish()


def test_stranger_cannot_start_next_rewards_period_with_zero_amount(rewards_manager, stranger):
    with reverts("manager: rewards disabled"):
        rewards_manager.start_next_rewards_period({"from": stranger})


def test_stranger_starts_next_rewards_period(rewards_manager, ldo_token, dao_agent, stranger):
    ldo_token.transfer(rewards_manager, rewards_amount, {"from": dao_agent})

    assert ldo_token.balanceOf(rewards_manager) > 0
    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == True

    rewards_manager.start_next_rewards_period({"from": stranger})

    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == False


def test_stranger_cannot_start_next_rewards_period_while_current_is_active(rewards_manager, ldo_token, dao_agent, stranger):
    if not rewards_manager.is_rewards_period_finished({"from": stranger}):
        chain.sleep(rewards_manager.period_finish() + 1)
        chain.mine()

        assert rewards_manager.is_rewards_period_finished({"from": stranger}) == True

    ldo_token.transfer(rewards_manager, rewards_amount, {"from": dao_agent})
    rewards_manager.start_next_rewards_period({"from": stranger})

    chain.sleep(1)
    chain.mine()

    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == False

    ldo_token.transfer(rewards_manager, rewards_amount, {"from": dao_agent})

    with reverts("manager: rewards period not finished"):
        rewards_manager.start_next_rewards_period({"from": stranger})


def test_stranger_can_start_next_rewards_period_after_current_is_finished(rewards_manager, ldo_token, dao_agent, stranger):
    if not rewards_manager.is_rewards_period_finished({"from": stranger}):
        chain.sleep(rewards_manager.period_finish() + 1)
        chain.mine()

        assert rewards_manager.is_rewards_period_finished({"from": stranger}) == True

    ldo_token.transfer(rewards_manager, rewards_amount, {"from": dao_agent})
    rewards_manager.start_next_rewards_period({"from": stranger})

    chain.sleep(initial_rewards_duration_sec * 2)
    chain.mine()

    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == True

    ldo_token.transfer(rewards_manager, rewards_amount, {"from": dao_agent})
    rewards_manager.start_next_rewards_period({"from": stranger})

    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == False


def test_stranger_cannot_recover_erc20(rewards_manager, ldo_token, stranger):
    with reverts("not permitted"):
        rewards_manager.recover_erc20(ldo_token, 0, {"from": stranger})


def test_owner_recovers_erc20_to_own_address(rewards_manager, ldo_token, dao_agent, ape):
    assert ldo_token.balanceOf(rewards_manager) == 0

    ldo_token.transfer(rewards_manager, rewards_amount, {"from": dao_agent})

    assert ldo_token.balanceOf(rewards_manager) == rewards_amount

    tx = rewards_manager.recover_erc20(ldo_token, rewards_amount, ape, {"from": ape})

    assert len(tx.events) == 1
    assert tx.events['ERC20TokenRecovered']['token'] == ldo_token
    assert tx.events['ERC20TokenRecovered']['amount'] == rewards_amount
    assert tx.events['ERC20TokenRecovered']['recipient'] == ape
    
    assert ldo_token.balanceOf(ape) == rewards_amount


def test_owner_recovers_erc20_to_stranger_address(rewards_manager, ldo_token, dao_agent, ape, stranger):
    assert ldo_token.balanceOf(rewards_manager) == 0

    ldo_token.transfer(rewards_manager, rewards_amount, {"from": dao_agent})

    assert ldo_token.balanceOf(rewards_manager) == rewards_amount

    tx = rewards_manager.recover_erc20(ldo_token, rewards_amount, stranger, {"from": ape})

    assert len(tx.events) == 1
    assert tx.events['ERC20TokenRecovered']['token'] == ldo_token
    assert tx.events['ERC20TokenRecovered']['amount'] == rewards_amount
    assert tx.events['ERC20TokenRecovered']['recipient'] == stranger

    assert ldo_token.balanceOf(stranger) == rewards_amount
