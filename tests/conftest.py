import pytest
from brownie import ZERO_ADDRESS, RewardsManager, FarmingRewards, MooniswapFactoryGovernance, Mooniswap
from utils.config import (
    ldo_token_address,
    steth_token_address,
    dai_address,
    one_inch_token_address,
    lido_dao_agent_address,
    lido_dao_voting_address,
    scale,
    initial_rewards_duration_sec
)

@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass


@pytest.fixture(scope="function")
def rewards_manager(ape, farming_rewards, ldo_token):
    rewards_manager_contract = RewardsManager.deploy(farming_rewards, {"from": ape})
    assert farming_rewards.addGift(ldo_token, initial_rewards_duration_sec, rewards_manager_contract, scale, {"from": ape})
    return rewards_manager_contract


@pytest.fixture(scope="function")
def mooniswap_factory(ape):
    return MooniswapFactoryGovernance.deploy(ZERO_ADDRESS, {"from": ape})


@pytest.fixture(scope="function")
def mooniswap(ape, mooniswap_factory):
    return Mooniswap.deploy(steth_token_address, dai_address, "stETH-DAI Liquidity Pool Token", "LP", mooniswap_factory, {"from": ape})


@pytest.fixture(scope="function")
def farming_rewards(ape, mooniswap, one_inch_token):
    farming_rewards_contract = FarmingRewards.deploy(mooniswap, one_inch_token, initial_rewards_duration_sec, ape, scale, {"from": ape})
    return farming_rewards_contract


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
    return accounts.at(lido_dao_voting_address, force=True)


@pytest.fixture(scope="module")
def dao_agent(interface):
    return interface.Agent(lido_dao_agent_address)
