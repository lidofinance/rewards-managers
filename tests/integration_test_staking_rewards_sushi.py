import pytest
from brownie import StakingRewardsSushi, reverts
from brownie.network import Chain


TEN_DAYS = 10 * 24 * 60 * 60
DEPOSIT_AMOUNT = 1000 * 10 ** 18


@pytest.mark.usefixtures("notify_reward_amount_sushi")
def test_deposit(
    ape, master_chef_v2, statking_rewards_sushi, lp_token_sushi, ldo_token
):
    pid = master_chef_v2.poolLength() - 1

    assert lp_token_sushi.balanceOf(ape) > DEPOSIT_AMOUNT
    lp_token_sushi.approve(master_chef_v2, DEPOSIT_AMOUNT, {"from": ape})
    tx = master_chef_v2.deposit(pid, DEPOSIT_AMOUNT, ape, {"from": ape})

    # validate that zero reward wasn't paid
    assert "RewardPaid" not in tx.events

    assert statking_rewards_sushi.totalSupply() == DEPOSIT_AMOUNT
    assert statking_rewards_sushi.balanceOf(ape) == DEPOSIT_AMOUNT
    assert statking_rewards_sushi.rewards(ape) == 0
    assert statking_rewards_sushi.userRewardPerTokenPaid(ape) == 0

    earned = statking_rewards_sushi.earned(ape)
    assert earned == 0

    chain = Chain()
    chain.sleep(TEN_DAYS)  # keep tokens in pool for 10 days
    chain.mine()

    earned = statking_rewards_sushi.earned(ape)
    expected_profit = statking_rewards_sushi.rewardRate() * TEN_DAYS

    print(earned, expected_profit, statking_rewards_sushi.rewardRate())
    assert abs(earned - expected_profit) < 2 * statking_rewards_sushi.rewardRate()


@pytest.mark.usefixtures("notify_reward_amount_sushi")
def test_withdraw(
    ape, stranger, master_chef_v2, statking_rewards_sushi, lp_token_sushi, ldo_token
):
    "After withdraw user must receive reward for period from deposit to withdraw"
    "Current user rewards must be zeroing"
    # test some preconditions
    assert ldo_token.balanceOf(stranger) == 0

    # do deposit
    pid = master_chef_v2.poolLength() - 1
    assert lp_token_sushi.balanceOf(ape) > DEPOSIT_AMOUNT
    lp_token_sushi.approve(master_chef_v2, DEPOSIT_AMOUNT, {"from": ape})
    master_chef_v2.deposit(pid, DEPOSIT_AMOUNT, ape, {"from": ape})
    assert statking_rewards_sushi.balanceOf(ape) == DEPOSIT_AMOUNT

    # wait for 10 days before withdraw
    chain = Chain()
    chain.sleep(TEN_DAYS)
    chain.mine()

    earned = statking_rewards_sushi.earned(ape)

    # do withdraw
    tx = master_chef_v2.withdraw(pid, DEPOSIT_AMOUNT // 2, stranger, {"from": ape})

    # validate that reward was paid
    assert "RewardPaid" in tx.events
    assert tx.events["RewardPaid"]["user"] == ape
    assert tx.events["RewardPaid"]["recipient"] == stranger
    assert (
        abs(tx.events["RewardPaid"]["reward"] - earned)
        < statking_rewards_sushi.rewardRate()
    )
    assert ldo_token.balanceOf(stranger) == tx.events["RewardPaid"]["reward"]

    # validate that balance was updated correctly
    assert statking_rewards_sushi.balanceOf(ape) == DEPOSIT_AMOUNT // 2
    assert statking_rewards_sushi.balanceOf(stranger) == 0

    # validate that reward and earned was reset
    assert statking_rewards_sushi.rewards(ape) == 0
    assert statking_rewards_sushi.earned(ape) == 0


@pytest.mark.usefixtures("notify_reward_amount_sushi")
def test_harvest_no_rewards(
    ape, stranger, master_chef_v2, statking_rewards_sushi, ldo_token
):
    # test some preconditions
    assert ldo_token.balanceOf(stranger) == 0

    assert statking_rewards_sushi.balanceOf(stranger) == 0
    assert statking_rewards_sushi.rewards(ape) == 0
    assert statking_rewards_sushi.earned(ape) == 0

    pid = master_chef_v2.poolLength() - 1
    tx = master_chef_v2.harvest(pid, stranger, {"from": ape})

    assert "RewardPaid" not in tx.events
    assert ldo_token.balanceOf(stranger) == 0


@pytest.mark.usefixtures("notify_reward_amount_sushi")
def test_harvest(
    ape, stranger, master_chef_v2, statking_rewards_sushi, lp_token_sushi, ldo_token
):
    # test some preconditions
    assert ldo_token.balanceOf(stranger) == 0

    # do deposit
    pid = master_chef_v2.poolLength() - 1
    assert lp_token_sushi.balanceOf(ape) > DEPOSIT_AMOUNT
    lp_token_sushi.approve(master_chef_v2, DEPOSIT_AMOUNT, {"from": ape})
    master_chef_v2.deposit(pid, DEPOSIT_AMOUNT, ape, {"from": ape})
    assert statking_rewards_sushi.balanceOf(ape) == DEPOSIT_AMOUNT

    # wait for 10 days before harvest
    chain = Chain()
    chain.sleep(TEN_DAYS)
    chain.mine()

    earned = statking_rewards_sushi.earned(ape)

    # do harvest
    tx = master_chef_v2.harvest(pid, stranger, {"from": ape})

    assert "RewardPaid" in tx.events
    assert tx.events["RewardPaid"]["user"] == ape
    assert tx.events["RewardPaid"]["recipient"] == stranger
    assert (
        abs(tx.events["RewardPaid"]["reward"] - earned)
        < statking_rewards_sushi.rewardRate()
    )
    assert ldo_token.balanceOf(stranger) == tx.events["RewardPaid"]["reward"]

    # validate that reward and earned was reset
    assert statking_rewards_sushi.rewards(ape) == 0
    assert statking_rewards_sushi.earned(ape) == 0


@pytest.mark.usefixtures("notify_reward_amount_sushi")
def test_withdraw_and_harvest(
    ape, stranger, ldo_token, master_chef_v2, lp_token_sushi, statking_rewards_sushi
):
    # test some preconditions
    assert ldo_token.balanceOf(stranger) == 0

    # do deposit
    pid = master_chef_v2.poolLength() - 1
    assert lp_token_sushi.balanceOf(ape) > DEPOSIT_AMOUNT
    lp_token_sushi.approve(master_chef_v2, DEPOSIT_AMOUNT, {"from": ape})
    master_chef_v2.deposit(pid, DEPOSIT_AMOUNT, ape, {"from": ape})
    assert statking_rewards_sushi.balanceOf(ape) == DEPOSIT_AMOUNT

    # wait for 10 days before withdraw and harvest
    chain = Chain()
    chain.sleep(TEN_DAYS)
    chain.mine()

    earned = statking_rewards_sushi.earned(ape)

    tx = master_chef_v2.withdrawAndHarvest(
        pid, DEPOSIT_AMOUNT // 2, stranger, {"from": ape}
    )

    assert "RewardPaid" in tx.events
    assert tx.events["RewardPaid"]["user"] == ape
    assert tx.events["RewardPaid"]["recipient"] == stranger
    assert (
        abs(tx.events["RewardPaid"]["reward"] - earned)
        < statking_rewards_sushi.rewardRate()
    )
    assert ldo_token.balanceOf(stranger) == tx.events["RewardPaid"]["reward"]

    # validate that balance was updated correctly
    assert statking_rewards_sushi.balanceOf(ape) == DEPOSIT_AMOUNT // 2
    assert statking_rewards_sushi.balanceOf(stranger) == 0

    # validate that reward and earned was reset
    assert statking_rewards_sushi.rewards(ape) == 0
    assert statking_rewards_sushi.earned(ape) == 0


@pytest.mark.usefixtures("notify_reward_amount_sushi")
def test_withdraw_and_harvest_empty_balance(
    ape, stranger, master_chef_v2, statking_rewards_sushi, ldo_token
):
    # test some preconditions
    assert ldo_token.balanceOf(stranger) == 0

    assert statking_rewards_sushi.balanceOf(stranger) == 0
    assert statking_rewards_sushi.rewards(ape) == 0
    assert statking_rewards_sushi.earned(ape) == 0

    pid = master_chef_v2.poolLength() - 1
    tx = master_chef_v2.withdrawAndHarvest(pid, 0, stranger, {"from": ape})

    assert "RewardPaid" not in tx.events
    assert ldo_token.balanceOf(stranger) == 0

    # validate that balance was updated correctly
    assert statking_rewards_sushi.balanceOf(ape) == 0
    assert statking_rewards_sushi.balanceOf(stranger) == 0

    # validate that reward and earned was reset
    assert statking_rewards_sushi.rewards(ape) == 0
    assert statking_rewards_sushi.earned(ape) == 0


@pytest.mark.usefixtures("notify_reward_amount_sushi")
def test_emergency_withdraw(
    ape, stranger, ldo_token, lp_token_sushi, master_chef_v2, statking_rewards_sushi
):
    # test some preconditions
    assert ldo_token.balanceOf(stranger) == 0

    # do deposit
    pid = master_chef_v2.poolLength() - 1
    assert lp_token_sushi.balanceOf(ape) > DEPOSIT_AMOUNT
    lp_token_sushi.approve(master_chef_v2, DEPOSIT_AMOUNT, {"from": ape})
    master_chef_v2.deposit(pid, DEPOSIT_AMOUNT, ape, {"from": ape})
    assert statking_rewards_sushi.balanceOf(ape) == DEPOSIT_AMOUNT

    # wait for 10 days before emergency withdraw
    chain = Chain()
    chain.sleep(TEN_DAYS)
    chain.mine()

    earned = statking_rewards_sushi.earned(ape)

    tx = master_chef_v2.withdrawAndHarvest(
        pid, DEPOSIT_AMOUNT // 2, stranger, {"from": ape}
    )

    assert "RewardPaid" in tx.events
    assert tx.events["RewardPaid"]["user"] == ape
    assert tx.events["RewardPaid"]["recipient"] == stranger
    assert (
        abs(tx.events["RewardPaid"]["reward"] - earned)
        < statking_rewards_sushi.rewardRate()
    )
    assert ldo_token.balanceOf(stranger) == tx.events["RewardPaid"]["reward"]

    # validate that balance was updated correctly
    assert statking_rewards_sushi.balanceOf(ape) == DEPOSIT_AMOUNT // 2
    assert statking_rewards_sushi.balanceOf(stranger) == 0

    # validate that reward and earned was reset
    assert statking_rewards_sushi.rewards(ape) == 0
    assert statking_rewards_sushi.earned(ape) == 0
