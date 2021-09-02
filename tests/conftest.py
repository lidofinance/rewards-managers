import pytest
from brownie import ZERO_ADDRESS, RewardsManager
from utils.config import (
    gift_index,
    ldo_token_address,
    steth_token_address,
    dai_address,
    one_inch_token_address,
    lido_dao_agent_address,
    farming_rewards_address,
    farming_rewards_owner,
    mooniswap_address
)


@pytest.fixture(scope="function")
def rewards_manager(ape, farming_rewards):
    manager = RewardsManager.deploy(farming_rewards, {"from": ape})

    farming_rewards.setRewardDistribution(gift_index, manager, {"from": farming_rewards_owner})

    return manager


@pytest.fixture(scope="function")
def mooniswap(interface):
    return interface.Mooniswap(mooniswap_address)


@pytest.fixture(scope="function")
def farming_rewards(interface):
    return interface.FarmingRewards(farming_rewards_address)


@pytest.fixture(scope="module")
def ape(accounts):
    return accounts[0]


@pytest.fixture(scope="module")
def stranger(accounts):
    return accounts[1]


@pytest.fixture(scope="module")
def ldo_token(interface):
    return interface.ERC20(ldo_token_address)


@pytest.fixture(scope="module")
def steth_token(interface):
    return interface.ERC20(steth_token_address)


@pytest.fixture(scope="module")
def dai_token(interface):
    return interface.ERC20(dai_address)


@pytest.fixture(scope="module")
def one_inch_token(interface):
    return interface.ERC20(one_inch_token_address)


@pytest.fixture(scope="module")
def dao_voting_impersonated(accounts):
    return accounts.at("0x2e59A20f205bB85a89C53f1936454680651E618e", force=True)


@pytest.fixture(scope="module")
def dao_agent(interface):
    return interface.Agent(lido_dao_agent_address)
