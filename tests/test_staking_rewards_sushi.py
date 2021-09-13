import pytest
from brownie import StakingRewardsSushi, reverts, chain
from utils.config import sushi_master_chef_v2, initial_rewards_duration_sec

DEPOSIT_AMOUNT = 1000 * 10 ** 18


def test_deploy(ape, accounts, ldo_token, lp_token_sushi_mock):
    owner = accounts[2]
    rewards_distribution = accounts[3]
    staking_token = lp_token_sushi_mock
    rewards_token = ldo_token

    contract = StakingRewardsSushi.deploy(
        owner,
        rewards_distribution,
        rewards_token,
        staking_token,
        initial_rewards_duration_sec,
        {"from": ape},
    )

    assert contract.MASTERCHEF_V2() == sushi_master_chef_v2
    assert contract.rewardsToken() == rewards_token
    assert contract.stakingToken() == staking_token
    assert contract.periodFinish() == 0
    assert contract.rewardRate() == 0
    assert contract.rewardsDuration() == initial_rewards_duration_sec
    assert contract.lastUpdateTime() == 0
    assert contract.rewardPerTokenStored() == 0


def test_total_supply(ape, staking_rewards_sushi, lp_token_sushi_mock, master_chef_v2):
    "Must return lpToken balance of MasterChefV2 contract"
    assert lp_token_sushi_mock.balanceOf(ape) >= DEPOSIT_AMOUNT
    assert lp_token_sushi_mock.balanceOf(master_chef_v2) == 0
    assert (
        lp_token_sushi_mock.balanceOf(master_chef_v2)
        == staking_rewards_sushi.totalSupply()
    )
    lp_token_sushi_mock.transfer(master_chef_v2, DEPOSIT_AMOUNT, {"from": ape})

    assert lp_token_sushi_mock.balanceOf(master_chef_v2) == DEPOSIT_AMOUNT
    assert (
        lp_token_sushi_mock.balanceOf(master_chef_v2)
        == staking_rewards_sushi.totalSupply()
    )


def test_on_sushi_reward_called_by_stranger(stranger, staking_rewards_sushi):
    with reverts("Only MCV2 can call this function."):
        staking_rewards_sushi.onSushiReward(
            0, stranger, stranger, 0, 0, {"from": stranger}
        )


def test_on_sushi_reward_called_with_wrong_pid(
    stranger, master_chef_v2, staking_rewards_sushi
):
    prev_pid = master_chef_v2.poolLength() - 2  # poolLength contains value pid + 1
    with reverts("Wrong PID."):
        staking_rewards_sushi.onSushiReward(
            prev_pid, stranger, stranger, 0, 0, {"from": master_chef_v2}
        )


def test_on_sushi_reward_updates_balance(
    stranger, master_chef_v2, staking_rewards_sushi
):
    pool_pid = master_chef_v2.poolLength() - 1
    staking_rewards_sushi.onSushiReward(
        pool_pid, stranger, stranger, 0, DEPOSIT_AMOUNT, {"from": master_chef_v2}
    )
    assert staking_rewards_sushi.balanceOf(stranger) == DEPOSIT_AMOUNT


@pytest.mark.usefixtures("notify_reward_amount_sushi")
def test_pending_tokens_called_with_wrong_pid(
    ape, master_chef_v2, staking_rewards_sushi, lp_token_sushi_mock
):
    "Must return tuple with empty arrays"
    pid = master_chef_v2.poolLength() - 1
    wrong_pid = pid - 1
    assert wrong_pid > 0 and wrong_pid != pid

    staking_rewards_sushi.onSushiReward(
        pid, ape, ape, 0, DEPOSIT_AMOUNT, {"from": master_chef_v2}
    )

    # simulate deposit to make rewardPerToken > 0
    lp_token_sushi_mock.transfer(master_chef_v2, DEPOSIT_AMOUNT, {"from": ape})
    #  wait some time till reward will become greater than 0
    chain.sleep(60)
    chain.mine()

    assert staking_rewards_sushi.rewardPerToken() > 0

    pending_tokens, pending_amounts = staking_rewards_sushi.pendingTokens(
        wrong_pid, ape, 0
    )
    assert len(pending_tokens) == 0
    assert len(pending_amounts) == 0


@pytest.mark.usefixtures("notify_reward_amount_sushi")
def test_pending_tokens(
    ape, master_chef_v2, staking_rewards_sushi, lp_token_sushi_mock, ldo_token
):
    "Must return [rewardsToken] and [earned(user)] for pendingTokens and pendingAmounts values correspondingly"
    pid = master_chef_v2.poolLength() - 1
    staking_rewards_sushi.onSushiReward(
        pid, ape, ape, 0, DEPOSIT_AMOUNT, {"from": master_chef_v2}
    )

    # simulate deposit to make rewardPerToken > 0
    lp_token_sushi_mock.transfer(master_chef_v2, DEPOSIT_AMOUNT, {"from": ape})
    #  wait some time till reward will become greater than 0
    chain.sleep(60)
    chain.mine()

    assert staking_rewards_sushi.rewardPerToken() > 0

    pending_tokens, pending_amounts = staking_rewards_sushi.pendingTokens(pid, ape, 0)
    assert len(pending_tokens) == 1
    assert pending_tokens[0] == ldo_token

    assert len(pending_amounts) == 1
    assert pending_amounts[0] == staking_rewards_sushi.earned(ape)


@pytest.mark.usefixtures("notify_reward_amount_sushi")
def test_reward_per_second(staking_rewards_sushi):
    "Must return current rewardRate value if periodFinish not passed and 0 in other cases"
    assert staking_rewards_sushi.periodFinish() > chain[-1].timestamp
    assert staking_rewards_sushi.rewardPerSecond() == staking_rewards_sushi.rewardRate()

    chain.sleep(initial_rewards_duration_sec + 1)
    chain.mine()
    assert staking_rewards_sushi.periodFinish() < chain[-1].timestamp
    assert staking_rewards_sushi.rewardPerSecond() == 0


@pytest.mark.usefixtures("notify_reward_amount_sushi")
def test_reward_token(staking_rewards_sushi, ldo_token):
    assert staking_rewards_sushi.rewardToken() == staking_rewards_sushi.rewardsToken()
    assert staking_rewards_sushi.rewardToken() == ldo_token


def test_update_period_finish_called_by_stranger(stranger, staking_rewards_sushi):
    new_period_finish = chain[-1].timestamp + 7 * 24 * 60 * 60
    with reverts("Only the contract owner may perform this action"):
        staking_rewards_sushi.updatePeriodFinish(new_period_finish, {"from": stranger})


@pytest.mark.usefixtures("notify_reward_amount_sushi")
def test_update_period_finish(ape, staking_rewards_sushi):
    new_period_finish = chain[-1].timestamp + 7 * 24 * 60 * 60
    reward_rate = staking_rewards_sushi.rewardRate()
    assert staking_rewards_sushi.periodFinish() != new_period_finish
    staking_rewards_sushi.updatePeriodFinish(new_period_finish, {"from": ape})
    assert staking_rewards_sushi.periodFinish() == new_period_finish
    # validate that rewardRate stayed same
    assert staking_rewards_sushi.rewardRate() == reward_rate
