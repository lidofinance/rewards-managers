import pytest
from brownie import ZERO_ADDRESS, RewardsManager, FarmingRewards, Mooniswap, MooniswapFactoryGovernance, chain
from utils.config import ldo_token_address, steth_token_address, dai_address, one_inch_token_address

time_in_the_past = 1628687598
gift_index = 1


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
def farming_rewards(ape, mooniswap, steth_token, distributor, rewards_manager):
    contract = FarmingRewards.deploy(mooniswap, steth_token, 100000, distributor, 10, {"from": ape})
    contract.addGift(ldo_token_address, 100000, rewards_manager, 10, {"from": ape})
    return contract


@pytest.fixture(scope="module")
def ape(accounts):
    return accounts[0]


@pytest.fixture(scope="module")
def stranger(accounts):
    return accounts[1]


@pytest.fixture(scope="module")
def distributor(accounts):
    return accounts[2]


@pytest.fixture(scope="module")
def ldo_token(interface):
    return interface.ERC20(ldo_token_address)


@pytest.fixture(scope="module")
def one_inch_token(interface):
    return interface.ERC20(one_inch_token_address)


@pytest.fixture(scope="module")
def steth_token(interface):
    return interface.ERC20(steth_token_address)


@pytest.fixture(scope="function")
def set_rewards_contract(ape, farming_rewards, rewards_manager):
    rewards_manager.set_rewards_contract(farming_rewards, {"from": ape})


@pytest.fixture(scope="function")
def set_gift_index(ape, rewards_manager, gift_index):
    rewards_manager.set_gift_index(gift_index, {"from": ape})

