import pytest
from brownie import reverts, Wei, ZERO_ADDRESS
from brownie.network.state import Chain
from scripts.deploy import deploy_manager_and_rewards
from utils.config import initial_rewards_duration_sec


def test_owner_is_deployer(rewards_manager, ape):
    assert rewards_manager.owner() == ape


def test_stranger_can_not_transfer_ownership(rewards_manager, ape, stranger):
    with reverts("not permitted"):
        rewards_manager.transfer_ownership(stranger, {"from": stranger})


def test_ownership_can_be_transferred(rewards_manager, ape, stranger):
    rewards_manager.transfer_ownership(stranger, {"from": ape})
    assert rewards_manager.owner() == stranger


def test_ownership_can_be_transferred_to_zero_address(rewards_manager, ape):
    rewards_manager.transfer_ownership(ZERO_ADDRESS, {"from": ape})
    assert rewards_manager.owner() == ZERO_ADDRESS


@pytest.mark.usefixtures("set_rewards_contract")
def test_stranger_can_not_set_rewards_contract(rewards_manager, stranger):
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


def test_stranger_can_not_recover_erc20(rewards_manager, ldo_token, stranger):
    with reverts("not permitted"):
        rewards_manager.recover_erc20(ldo_token, {"from": stranger})


def test_owner_recovers_erc20(rewards_manager, ldo_token, ape):
    rewards_manager.recover_erc20(ldo_token, {"from": ape})


@pytest.mark.usefixtures("set_rewards_contract")
def test_stranger_can_check_is_rewards_period_finished(rewards_manager, stranger):
    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == True


def test_stranger_can_not_start_next_rewards_period_without_rewards_contract_set(
    rewards_manager, stranger
):
    with reverts("manager: rewards disabled"):
        rewards_manager.start_next_rewards_period({"from": stranger})


@pytest.mark.usefixtures("set_rewards_contract")
def test_stranger_can_not_start_next_rewards_period_with_zero_amount(
    rewards_manager, stranger, ape
):
    with reverts("manager: rewards disabled"):
        rewards_manager.start_next_rewards_period({"from": stranger})


@pytest.mark.usefixtures("set_rewards_contract")
def test_stranger_starts_next_rewards_period(
    rewards_manager, ldo_token, dao_agent, stranger
):
    rewards_amount = Wei("1 ether")
    ldo_token.transfer(rewards_manager, rewards_amount, {"from": dao_agent})
    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == True
    rewards_manager.start_next_rewards_period({"from": stranger})
    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == False


@pytest.mark.usefixtures("set_rewards_contract")
def test_stranger_can_not_start_next_rewards_period_while_current_is_active(
    rewards_manager, ldo_token, dao_agent, stranger
):
    rewards_amount = Wei("1 ether")
    ldo_token.transfer(rewards_manager, rewards_amount, {"from": dao_agent})
    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == True
    rewards_manager.start_next_rewards_period({"from": stranger})
    chain = Chain()
    chain.sleep(1)
    chain.mine()

    ldo_token.transfer(rewards_manager, rewards_amount, {"from": dao_agent})
    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == False
    with reverts("manager: rewards period not finished"):
        rewards_manager.start_next_rewards_period({"from": stranger})


@pytest.mark.usefixtures("set_rewards_contract")
def test_stranger_can_start_next_rewards_period_after_current_is_finished(
    rewards_manager, staking_rewards_sushi, ldo_token, dao_agent, stranger
):
    rewards_amount = Wei("1 ether")
    ldo_token.transfer(rewards_manager, rewards_amount, {"from": dao_agent})
    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == True
    rewards_manager.start_next_rewards_period({"from": stranger})
    chain = Chain()
    chain.sleep(initial_rewards_duration_sec)
    chain.mine()

    ldo_token.transfer(rewards_manager, rewards_amount, {"from": dao_agent})
    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == True
    rewards_manager.start_next_rewards_period({"from": stranger})
    assert rewards_manager.is_rewards_period_finished({"from": stranger}) == False
