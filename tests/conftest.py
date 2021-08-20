import pytest
from brownie import ZERO_ADDRESS, RewardsManager, StubFarmingRewards, chain
from utils.config import ldo_token_address

time_in_the_past = 1628687598
gift_index = 1


@pytest.fixture(scope="function")
def rewards_manager(ape):
    return RewardsManager.deploy({"from": ape})


@pytest.fixture(scope="function")
def farming_rewards(ape):
    return StubFarmingRewards.deploy(100, gift_index, time_in_the_past, {"from": ape})


@pytest.fixture(scope="module")
def ape(accounts):
    return accounts[0]


@pytest.fixture(scope="module")
def stranger(accounts):
    return accounts[1]


@pytest.fixture(scope="module")
def ldo_token(interface):
    return interface.ERC20(ldo_token_address)


@pytest.fixture(scope="function")
def set_rewards_contract(ape, farming_rewards, rewards_manager):
    rewards_manager.set_rewards_contract(farming_rewards, {"from": ape})


@pytest.fixture(scope="function")
def set_gift_index(ape, gift_index):
    rewards_manager.set_gift_index(gift_index, {"from": ape})

