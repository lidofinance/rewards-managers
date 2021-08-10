import pytest
from brownie import Wei, ZERO_ADDRESS, DropToken, StakingRewardsSushi
from scripts.deploy import deploy_manager_and_rewards
from utils.config import (
    ldo_token_address,
    lido_dao_agent_address,
    lido_dao_finance_address,
    lido_dao_voting_address,
    lido_dao_token_manager_address,
    sushi_master_chef_v2,
    initial_rewards_duration_sec,
    lp_token_address,
    sushiswap_router_address,
    wsteth_address,
    dai_address,
)


@pytest.fixture
def wsteth_token(interface):
    return interface.ERC20(wsteth_address)


@pytest.fixture
def dai_token(interface):
    return interface.ERC20(dai_address)


@pytest.fixture(scope="function")
def lp_token_sushi(interface):
    return interface.UniswapV2Pair(lp_token_address)


@pytest.fixture(scope="function")
def lp_token_sushi_mock(ape):
    return DropToken.deploy("SUSHI LP", "SLP", 18, 1000000 * 10 ** 18, {"from": ape})


@pytest.fixture
def sushiswap_router(interface):
    return interface.UniswapV2Router02(sushiswap_router_address)


@pytest.fixture(scope="function")
def master_chef_v2(interface):
    return interface.MasterChefV2(sushi_master_chef_v2)


@pytest.fixture()
def master_chef_v2_owner(accounts):
    return accounts.at("0x19b3eb3af5d93b77a5619b047de0eed7115a19e7", force=True)


@pytest.fixture(scope="function")
def staking_rewards_sushi(
    ape,
    rewards_manager,
    lp_token_sushi_mock,
    ldo_token,
    master_chef_v2,
    master_chef_v2_owner,
):
    staking_rewards_sushi = StakingRewardsSushi.deploy(
        ape,
        rewards_manager,
        ldo_token,
        lp_token_sushi_mock,
        initial_rewards_duration_sec,
        {"from": ape},
    )
    # create pool in master chef v2 for new rewarder
    master_chef_v2.add(
        100, lp_token_sushi_mock, staking_rewards_sushi, {"from": master_chef_v2_owner}
    )
    return staking_rewards_sushi


@pytest.fixture(scope="module")
def ape(accounts):
    return accounts[0]


@pytest.fixture(scope="function")
def stranger(accounts, ldo_token, dao_agent):
    stranger_account = accounts[9]
    balance = ldo_token.balanceOf(stranger_account)
    # Reset balance of stranger if he has some LDO from prev tests
    if balance > 0:
        ldo_token.transfer(dao_agent, balance, {"from": stranger_account})
    return accounts[9]


@pytest.fixture(scope="module")
def dao_voting_impersonated(accounts):
    return accounts.at("0x2e59A20f205bB85a89C53f1936454680651E618e", force=True)


@pytest.fixture(scope="module")
def dao_voting(interface):
    return interface.Voting(lido_dao_voting_address)


@pytest.fixture(scope="module")
def dao_token_manager(interface):
    return interface.TokenManager(lido_dao_token_manager_address)


@pytest.fixture(scope="module")
def dao_finance(interface):
    return interface.Finance(lido_dao_finance_address)


# Lido DAO Agent app
@pytest.fixture(scope="module")
def dao_agent(interface):
    return interface.Agent(lido_dao_agent_address)


@pytest.fixture(scope="module")
def ldo_token(interface):
    return interface.ERC20(ldo_token_address)


@pytest.fixture(scope="function")
def rewards_manager(RewardsManager, ape):
    return RewardsManager.deploy({"from": ape})


@pytest.fixture
def notify_reward_amount_sushi(
    rewards_manager, dao_agent, staking_rewards_sushi, ldo_token
):
    reward_amount = 100_000 * 10 ** 18
    ldo_token.approve(staking_rewards_sushi, reward_amount, {"from": dao_agent})
    staking_rewards_sushi.notifyRewardAmount(
        reward_amount, dao_agent, {"from": rewards_manager}
    )
    assert (
        staking_rewards_sushi.rewardRate()
        == reward_amount // initial_rewards_duration_sec
    )
    assert staking_rewards_sushi.periodFinish() != 0


@pytest.fixture(scope="function")
def set_rewards_contract(ape, staking_rewards_sushi, rewards_manager):
    rewards_manager.set_rewards_contract(staking_rewards_sushi, {"from": ape})
