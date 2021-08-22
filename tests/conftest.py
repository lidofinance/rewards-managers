import pytest
from brownie import ZERO_ADDRESS, RewardsManager, FarmingRewards, Mooniswap, MooniswapFactoryGovernance
from utils.config import ldo_token_address, steth_token_address, dai_address, one_inch_token_address


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
    farming_rewards_contract = FarmingRewards.deploy(mooniswap, one_inch_token, 200000, ape, 10, {"from": ape})
    farming_rewards_contract.addGift(ldo_token, 200000, rewards_manager, 10, {"from": ape})
    return farming_rewards_contract


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
def steth_token(interface):
    return interface.ERC20(steth_token_address)


@pytest.fixture(scope="module")
def one_inch_token(interface):
    return interface.ERC20(one_inch_token_address)


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

