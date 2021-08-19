import pytest
from brownie import ZERO_ADDRESS, RewardsManager, StubERC20, StubFarmingRewards
from utils.config import ldo_token_address

@pytest.fixture(scope="function")
def rewards_manager(ape):
    return RewardsManager.deploy({"from": ape})


@pytest.fixture(scope="function")
def rewards_token(ape):
    return StubERC20.deploy("Lido DAO Token", "LDO", 250000, {"from": ape})


@pytest.fixture(scope="function")
def farming_rewards(ape):
    return StubFarmingRewards.deploy(100, 1, 1628687598, {"from": ape})


@pytest.fixture(scope="module")
def ape(accounts):
    return accounts[0]


@pytest.fixture(scope="module")
def stranger(accounts):
    return accounts[1]


@pytest.fixture(scope="function")
def set_rewards_contract(ape, farming_rewards, rewards_manager):
    rewards_manager.set_rewards_contract(farming_rewards, {"from": ape})

