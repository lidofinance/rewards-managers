import pytest
from brownie import reverts, ZERO_ADDRESS, chain, accounts
import web3
from utils.config import ldo_token_address, lido_dao_agent_address


def test_owner_is_deployer(rewards_manager, ape):
    assert rewards_manager.owner() == ape


def test_stranger_cannot_transfer_ownership(rewards_manager, stranger):
    with reverts("not permitted"):
        rewards_manager.transfer_ownership(stranger, {"from": stranger})


def test_ownership_can_be_transferred(rewards_manager, ape, stranger):
    rewards_manager.transfer_ownership(stranger, {"from": ape})
    assert rewards_manager.owner() == stranger


def test_ownership_can_be_transferred_to_zero_address(rewards_manager, ape):
    rewards_manager.transfer_ownership(ZERO_ADDRESS, {"from": ape})
    assert rewards_manager.owner() == ZERO_ADDRESS


@pytest.mark.usefixtures("set_rewards_contract")
def test_stranger_cannot_set_rewards_contract(rewards_manager, stranger):
    assert rewards_manager.rewards_contract != ZERO_ADDRESS
    with reverts("not permitted"):
        rewards_manager.set_rewards_contract(ZERO_ADDRESS, {"from": stranger})


@pytest.mark.usefixtures("set_rewards_contract")
def test_owner_can_set_rewards_contract(rewards_manager, ape):
    assert rewards_manager.rewards_contract != ZERO_ADDRESS
    rewards_manager.set_rewards_contract(ZERO_ADDRESS, {"from": ape})
    assert rewards_manager.rewards_contract() == ZERO_ADDRESS


@pytest.mark.usefixtures("set_rewards_contract")
def test_owner_can_set_rewards_contract_to_zero_address(rewards_manager, ape):
    assert rewards_manager.rewards_contract != ZERO_ADDRESS
    rewards_manager.set_rewards_contract(ZERO_ADDRESS, {"from": ape})
    assert rewards_manager.rewards_contract() == ZERO_ADDRESS


@pytest.mark.usefixtures("set_rewards_contract")
def test_stranger_cannot_set_gift_index(rewards_manager, stranger, gift_index):
    assert rewards_manager.gift_index != gift_index
    with reverts("not permitted"):
        rewards_manager.set_gift_index(gift_index, {"from": stranger})


@pytest.mark.usefixtures("set_rewards_contract")
def test_owner_can_set_gift_index(rewards_manager, ape, gift_index):
    assert rewards_manager.gift_index != gift_index
    rewards_manager.set_gift_index(gift_index, {"from": ape})
    assert rewards_manager.gift_index() == gift_index


@pytest.mark.usefixtures("set_rewards_contract", "set_gift_index")
def test_is_rewards_period_finished(rewards_manager, farming_rewards, gift_index):
    assert (chain[-1].timestamp >= farming_rewards.tokenRewards(gift_index)[4]) == rewards_manager.is_rewards_period_finished()


@pytest.mark.usefixtures("set_rewards_contract", "set_gift_index")
def test_out_of_funding_date(rewards_manager, farming_rewards, gift_index):
    assert farming_rewards.tokenRewards(gift_index)[4] == rewards_manager.out_of_funding_date()


def test_start_next_rewards_period_with_zero_contract_address(rewards_manager, ape):
    with reverts("manager: rewards disabled"):
        rewards_manager.start_next_rewards_period({"from": ape})


@pytest.mark.usefixtures("set_rewards_contract", "set_gift_index")
def test_start_next_rewards_period_with_zero_balance(rewards_manager, ldo_token, ape):
    assert ldo_token.balanceOf(rewards_manager) == 0
    with reverts("manager: rewards disabled"):
        rewards_manager.start_next_rewards_period({"from": ape})


@pytest.mark.usefixtures("set_rewards_contract", "set_gift_index")
def test_start_next_rewards_period_with_rewards_period_not_finished(rewards_manager, farming_rewards, gift_index, ldo_token, ape):
    ldo_token.transfer(rewards_manager, 100, {"from": accounts.at(lido_dao_agent_address, force=True)})
    assert ldo_token.balanceOf(rewards_manager) > 0
    print(farming_rewards.tokenRewards(gift_index))          # FIXME to be deleted
    with reverts("manager: rewards period not finished"):
        rewards_manager.start_next_rewards_period({"from": ape})

        # (chain[-1].timestamp >= farming_rewards.tokenRewards(gift_index)[4]) != rewards_manager.is_rewards_period_finished()
