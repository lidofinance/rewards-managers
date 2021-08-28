import pytest
from brownie import ZERO_ADDRESS, RewardsManager, FarmingRewards, Mooniswap, MooniswapFactoryGovernance
from utils.config import (
    ldo_token_address,
    steth_token_address,
    dai_address,
    one_inch_token_address,
    rewards_amount,
    scale,
    lido_dao_agent_address,
    lido_dao_voting_address
)


@pytest.fixture(scope="function")
def rewards_manager(ape):
    return RewardsManager.deploy({"from": ape})


@pytest.fixture(scope="function")
def mooniswap_factory(ape):
    return MooniswapFactoryGovernance.deploy(ZERO_ADDRESS, {"from": ape})


@pytest.fixture(scope="function")
def mooniswap(ape, mooniswap_factory):
    return Mooniswap.deploy(steth_token_address, dai_address, "stETH-DAI Liquidity Pool Token", "LP", mooniswap_factory, {"from": ape})


@pytest.fixture(scope="function")
def farming_rewards(ape, mooniswap, one_inch_token, ldo_token, rewards_manager):
    farming_rewards_contract = FarmingRewards.deploy(mooniswap, one_inch_token, rewards_amount, ape, scale, {"from": ape})
    farming_rewards_contract.addGift(ldo_token, rewards_amount, rewards_manager, scale, {"from": ape})
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
    return accounts.at("0x2e59A20f205bB85a89C53f1936454680651E618e", force=True)


@pytest.fixture(scope="module")
def dao_voting(interface):
    return interface.Voting(lido_dao_voting_address)


@pytest.fixture(scope="module")
def dao_agent(interface):
    return interface.Agent(lido_dao_agent_address)


@pytest.fixture(scope="function")
def set_rewards_contract(ape, farming_rewards, rewards_manager):
    rewards_manager.set_rewards_contract(farming_rewards, {"from": ape})


@pytest.fixture(scope="function")
def set_gift_index(ape, rewards_manager, gift_index):
    rewards_manager.set_gift_index(gift_index, {"from": ape})

@pytest.fixture(scope="function")
def gift_index(farming_rewards):
    for i in range(10):     # could be changed
        if farming_rewards.tokenRewards(i)[0] == ldo_token_address:
            return i
    return 0
