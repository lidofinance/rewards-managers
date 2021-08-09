import pytest
import brownie


@pytest.fixture()
def rewards_manager(RewardsManager, ape):
    return RewardsManager.deploy({"from": ape})


def test_owner_recovers_erc20_with_zero_amount(
    rewards_manager, ldo_token, ape, dao_agent
):
    rewards_amount = brownie.Wei("1 ether")
    ape_balance_before = ldo_token.balanceOf(ape)
    ldo_token.transfer(rewards_manager, rewards_amount, {"from": dao_agent})
    tx = rewards_manager.recover_erc20(ldo_token, 0, {"from": ape})
    assert len(tx.events) == 0

    ape_balance_after = ldo_token.balanceOf(ape)
    assert ape_balance_before == ape_balance_after
    assert ldo_token.balanceOf(rewards_manager) == rewards_amount


def test_owner_recovers_erc20_with_balance(
    rewards_manager, ldo_token, dao_agent, ape, stranger
):
    recipient = stranger
    transfer_amount = brownie.Wei("1 ether")
    recover_amount = brownie.Wei("0.5 ether")
    ldo_token.transfer(rewards_manager, transfer_amount, {"from": dao_agent})
    assert ldo_token.balanceOf(rewards_manager) == transfer_amount

    recipient_balance_before = ldo_token.balanceOf(recipient)
    tx = rewards_manager.recover_erc20(
        ldo_token, recover_amount, recipient, {"from": ape}
    )
    recipient_balance_after = ldo_token.balanceOf(recipient)

    assert ldo_token.balanceOf(rewards_manager) == transfer_amount - recover_amount
    assert recipient_balance_after - recipient_balance_before == recover_amount
    assert len(tx.events) == 1
    assert tx.events[0].name == "Transfer"
    assert tx.events[0]["_from"] == rewards_manager
    assert tx.events[0]["_to"] == recipient
    assert tx.events[0]["_value"] == recover_amount


def test_owner_recovers_erc20_to_the_caller_by_default(
    rewards_manager, ldo_token, dao_agent, ape
):
    transfer_amount = brownie.Wei("1 ether")
    ldo_token.transfer(rewards_manager, transfer_amount, {"from": dao_agent})

    recipient_balance_before = ldo_token.balanceOf(ape)
    tx = rewards_manager.recover_erc20(ldo_token, transfer_amount, {"from": ape})
    recipient_balance_after = ldo_token.balanceOf(ape)

    assert ldo_token.balanceOf(rewards_manager) == 0
    assert recipient_balance_after - recipient_balance_before == transfer_amount
    assert len(tx.events) == 1
    assert tx.events[0].name == "Transfer"
    assert tx.events[0]["_from"] == rewards_manager
    assert tx.events[0]["_to"] == ape
    assert tx.events[0]["_value"] == transfer_amount


def test_recover_erc20_not_enough_balance(rewards_manager, ldo_token, dao_agent, ape):
    transfer_amount = brownie.Wei("1 ether")
    recover_amount = brownie.Wei("2 ether")
    ldo_token.transfer(rewards_manager, transfer_amount, {"from": dao_agent})

    recipient_balance_before = ldo_token.balanceOf(ape)
    with brownie.reverts("token transfer failed"):
        rewards_manager.recover_erc20(ldo_token, recover_amount, {"from": ape})
