import pytest
from brownie import reverts, chain
from brownie.network.state import Chain
from math import floor

rewards_limit = 25 * 1000 * 10**18
rewards_period = 3600 * 24 * 7


def test_init(rewards_manager, ldo_agent, balancer_allocator, merkle_contract):
    assert rewards_manager.owner() == ldo_agent
    assert rewards_manager.allocator() == balancer_allocator
    assert rewards_manager.rewards_contract() == merkle_contract
    assert rewards_manager.rewards_limit_per_period() == rewards_limit


def test_transfer_ownership(rewards_manager, ldo_agent, stranger, helpers):
    with reverts():
        rewards_manager.transfer_ownership(stranger, {"from": stranger})

    assert rewards_manager.owner() == ldo_agent
    tx = rewards_manager.transfer_ownership(stranger, {"from": ldo_agent})
    assert rewards_manager.owner() == stranger

    helpers.assert_single_event_named("OwnerChanged", tx, {"new_owner": stranger})


def test_change_allocator(rewards_manager, ldo_agent, balancer_allocator, stranger, helpers):
    with reverts():
        rewards_manager.change_allocator(stranger, {"from": stranger})

    assert rewards_manager.allocator() == balancer_allocator
    tx = rewards_manager.change_allocator(stranger, {"from": ldo_agent})
    assert rewards_manager.allocator() == stranger

    helpers.assert_single_event_named("AllocatorChanged", tx, {"new_allocator": stranger})

@pytest.mark.parametrize(
    'period', 
    [
        rewards_period, 
        floor(0.5*rewards_period), 
        floor(0.9*rewards_period), 
        floor(1.1*rewards_period), 
        floor(2.5*rewards_period)
    ]
)
def test_allowance_basic_calculation(rewards_manager, period):
    chain = Chain()

    assert rewards_manager.allowance() == 0
    chain.sleep(period)
    chain.mine()
    assert rewards_manager.allowance() == floor(period/rewards_period) * rewards_limit
    chain.sleep(period)
    chain.mine()
    assert rewards_manager.allowance() == floor(2 * period/rewards_period) * rewards_limit
    

def test_allowance_paused_calculation(rewards_manager, ldo_agent):
    assert rewards_manager.allowance() == 0
    chain.sleep(floor(1.5 * rewards_period))
    chain.mine()
    assert rewards_manager.allowance() == rewards_limit
    rewards_manager.pause({"from": ldo_agent})
    assert rewards_manager.allowance() == rewards_limit
    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.allowance() == rewards_limit

    rewards_manager.unpause({"from": ldo_agent})
    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.allowance() == 2 * rewards_limit


def test_allowance_calculation_with_changed_rewards_limit(rewards_manager, ldo_agent):
    assert rewards_manager.allowance() == 0
    chain.sleep(floor(1.5 * rewards_period))
    chain.mine()
    assert rewards_manager.allowance() == rewards_limit

    rewards_manager.change_rewards_limit(2 * rewards_limit, {"from": ldo_agent})
    assert rewards_manager.allowance() == rewards_limit
    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.allowance() == rewards_limit + 2 * rewards_limit

    rewards_manager.change_rewards_limit(0.5 * rewards_limit, {"from": ldo_agent})
    assert rewards_manager.allowance() == rewards_limit + 2 * rewards_limit
    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.allowance() == rewards_limit + 2 * rewards_limit + 0.5 * rewards_limit


def test_change_rewards_limit(rewards_manager, ldo_agent, stranger, helpers):
    assert rewards_manager.rewards_limit_per_period() == rewards_limit

    chain = Chain()

    assert rewards_manager.allowance() == 0
    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.allowance() == rewards_limit

    with reverts():
        rewards_manager.change_rewards_limit(2 * rewards_limit, {"from": stranger})

    tx = rewards_manager.change_rewards_limit(2 * rewards_limit, {"from": ldo_agent})
    assert rewards_manager.rewards_limit_per_period() == 2 * rewards_limit
    helpers.assert_single_event_named("RewardsLimitChanged", tx, {"new_limit": 2 * rewards_limit})

    assert rewards_manager.allowance() == rewards_limit
    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.allowance() == (1 + 2) * rewards_limit


def test_pause(rewards_manager, ldo_agent, stranger, helpers, balancer_allocator):
    assert rewards_manager.is_paused() == False

    chain = Chain()

    rewards_manager.seed_allocations(0, '', 0, {"from": balancer_allocator})

    with reverts():
        rewards_manager.pause({"from": stranger})

    tx = rewards_manager.pause({"from": ldo_agent})
    helpers.assert_single_event_named("Paused", tx, {"actor": ldo_agent})
    assert rewards_manager.is_paused() == True

    assert rewards_manager.allowance() == 0

    with reverts():
        rewards_manager.seed_allocations(0, '', 0, {"from": balancer_allocator})

    with reverts():
        rewards_manager.unpause({"from": stranger})

    tx = rewards_manager.unpause({"from": ldo_agent})
    helpers.assert_single_event_named("Unpaused", tx, {"actor": ldo_agent})
    assert rewards_manager.is_paused() == False

    rewards_manager.seed_allocations(0, '', 0, {"from": balancer_allocator})


def test_change_allowance_any_address(
    rewards_manager, 
    ldo_agent, 
    ldo_token, 
    stranger, 
    helpers
):

    chain = Chain()
    assert ldo_token.allowance(rewards_manager, stranger) == 0

    with reverts():
        rewards_manager.change_allowance(
            stranger, 
            10, 
            {"from": stranger}
        )

    tx = rewards_manager.change_allowance(
        stranger, 
        10,
        {"from": ldo_agent}
    )
    helpers.assert_single_event_named(
        "AllowanceChanged", 
        tx, 
        {"spender": stranger, "new_allowance": 10}
    )
    assert ldo_token.allowance(rewards_manager, stranger) == 10


def test_change_allowance(rewards_manager, ldo_agent, stranger, helpers):

    chain = Chain()
    assert rewards_manager.allowance() == 0

    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.allowance() == rewards_limit

    with reverts():
        rewards_manager.change_allowance(
            rewards_manager.rewards_contract(), 
            10, 
            {"from": stranger}
        )

    tx = rewards_manager.change_allowance(
        rewards_manager.rewards_contract(), 
        10, 
        {"from": ldo_agent}
    )
    helpers.assert_single_event_named(
        "AllowanceChanged", 
        tx, 
        {"spender": rewards_manager.rewards_contract(), "new_allowance": 10}
    )
    assert rewards_manager.allowance() == 10


def test_seed_allocations(
    rewards_manager,
    ldo_agent,
    ldo_token,
    stranger,
    helpers,
    dao_treasury,
    balancer_allocator
):
    chain = Chain()

    with reverts():
        rewards_manager.seed_allocations(0, '', 0, {"from": stranger})

    rewards_manager.pause({"from": ldo_agent})
    with reverts():
        rewards_manager.seed_allocations(0, '', 0, {"from": balancer_allocator})
    rewards_manager.unpause({"from": ldo_agent})


    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.allowance() == rewards_limit

    ldo_token.transfer(rewards_manager, 10000 * 10**18, {"from": dao_treasury})
    assert ldo_token.balanceOf(rewards_manager) == 10000 * 10**18
    
    with reverts('manager: reward token balance is low'):
        rewards_manager.seed_allocations(0, '', 25000 * 10**18, {"from": balancer_allocator})

    ldo_token.transfer(rewards_manager, 20000 * 10**18, {"from": dao_treasury})
    assert ldo_token.balanceOf(rewards_manager) == 30000 * 10**18

    with reverts('manager: not enought amount approved'):
        rewards_manager.seed_allocations(0, '', 30000 * 10**18, {"from": balancer_allocator})

    tx = rewards_manager.seed_allocations(0, '', rewards_limit, {"from": balancer_allocator})
    helpers.assert_single_event_named("Allocation", tx, {"amount": rewards_limit})
    assert rewards_manager.allowance() == 0
    assert ldo_token.balanceOf(rewards_manager) == 5000 * 10**18
    assert ldo_token.balanceOf(rewards_manager.rewards_contract()) == rewards_limit


def test_recover_erc20(rewards_manager, ldo_agent, ldo_token, stranger, helpers, dao_treasury):
    ldo_token.transfer(rewards_manager, 100, {"from": dao_treasury})
    assert ldo_token.balanceOf(rewards_manager) == 100

    with reverts('manager: not permitted'):
        rewards_manager.recover_erc20(ldo_token, {"from": stranger})

    balance = ldo_token.balanceOf(ldo_agent)

    tx = rewards_manager.recover_erc20(ldo_token, {"from": ldo_agent})
    assert ldo_token.balanceOf(rewards_manager) == 0
    assert ldo_token.balanceOf(ldo_agent) == balance + 100
    helpers.assert_single_event_named(
        "ERC20TokenRecovered", 
        tx, 
        {"token": ldo_token, "amount": 100, "recipient": ldo_agent}
    )

def test_recover_erc20_empty_balance(
    rewards_manager, 
    ldo_agent, 
    ldo_token, 
    stranger, 
    helpers, 
    dao_treasury
):
    assert ldo_token.balanceOf(rewards_manager) == 0

    with reverts('manager: not permitted'):
        rewards_manager.recover_erc20(ldo_token, {"from": stranger})

    balance = ldo_token.balanceOf(ldo_agent)
    tx = rewards_manager.recover_erc20(ldo_token, {"from": ldo_agent})
    assert ldo_token.balanceOf(ldo_agent) == balance
    helpers.assert_no_events_named("ERC20TokenRecovered", tx)
