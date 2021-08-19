import pytest
from brownie import RewardsManager, reverts, ZERO_ADDRESS, chain
import web3
from conftest import farming_rewards, gift_index, time_in_the_past
from utils.config import ldo_token_address


@pytest.fixture(scope="function")
def rewards_manager(RewardsManager, ape):
    return RewardsManager.deploy({"from": ape})


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


def test_stranger_cannot_set_gift_index(rewards_manager, stranger):
    assert rewards_manager.gift_index != 0
    with reverts("not permitted"):
        rewards_manager.set_gift_index(0, {"from": stranger})


def test_owner_can_set_gift_index(rewards_manager, ape):
    assert rewards_manager.gift_index != 0
    rewards_manager.set_gift_index(0, {"from": ape})
    assert rewards_manager.gift_index() == 0


@pytest.mark.usefixtures("set_rewards_contract")
def test_is_rewards_period_finished(rewards_manager, farming_rewards, ape):
    gift_token, scale, duration, reward_distribution, period_finish, reward_rate, last_update_time, reward_per_token_stored = farming_rewards.tokenRewards(gift_index, {"from": ape})
    assert chain[-1].timestamp >= rewards_manager.is_rewards_period_finished()

