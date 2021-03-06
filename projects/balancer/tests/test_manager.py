import pytest
from brownie import reverts, chain
from math import floor

rewards_limit = 25 * 1000 * 10**18
rewards_period = 3600 * 24 * 7
MERKLE_CONTRACT = '0x884226c9f7b7205f607922E0431419276a64CF8f'


def test_init(rewards_manager, ldo_agent, balancer_allocator):
    assert rewards_manager.owner() == ldo_agent
    assert rewards_manager.allocator() == balancer_allocator
    assert rewards_manager.rewards_limit_per_period() == rewards_limit


def test_transfer_ownership(rewards_manager, ldo_agent, stranger, helpers):
    with reverts():
        rewards_manager.transfer_ownership(stranger, {"from": stranger})

    assert rewards_manager.owner() == ldo_agent
    tx = rewards_manager.transfer_ownership(stranger, {"from": ldo_agent})
    assert rewards_manager.owner() == stranger

    helpers.assert_single_event_named("OwnerChanged", tx, {"new_owner": stranger})


def test_transfer_reward_contract(rewards_manager, ldo_agent, stranger, helpers, merkle_contract):
    with reverts():
        rewards_manager.transfer_ownership(stranger, {"from": stranger})

    print(rewards_manager)
    print(merkle_contract.owner())
    assert merkle_contract.owner() == rewards_manager
    tx = rewards_manager.transfer_rewards_contract_ownership(stranger, {"from": ldo_agent})
    assert merkle_contract.owner() == stranger

    helpers.assert_single_event_named("RewardContractOwnershipTransfered", tx, {"new_owner": stranger})


def test_set_allocator(rewards_manager, ldo_agent, balancer_allocator, stranger, helpers):
    with reverts():
        rewards_manager.set_allocator(stranger, {"from": stranger})

    assert rewards_manager.allocator() == balancer_allocator
    tx = rewards_manager.set_allocator(stranger, {"from": ldo_agent})
    assert rewards_manager.allocator() == stranger

    helpers.assert_single_event_named("AllocatorChanged", tx, {"new_allocator": stranger})


@pytest.mark.parametrize(
    'period', 
    [
        rewards_period, 
        rewards_period - 1, 
        rewards_period + 1, 
        floor(0.5*rewards_period), 
        floor(0.9*rewards_period), 
        floor(2.5*rewards_period)
    ]
)
def test_allocations_limit_basic_calculation(rewards_manager, period):
    start_date = rewards_manager.last_accounted_period_start_date()
    assert rewards_manager.available_allocations() == 0
    chain.sleep(start_date + period - chain.time())
    chain.mine()
    assert rewards_manager.available_allocations() == floor(period/rewards_period) * rewards_limit
    chain.sleep(period)
    chain.mine()
    assert rewards_manager.available_allocations() == floor(2 * period/rewards_period) * rewards_limit
    

def test_allocations_limit_paused_calculation(rewards_manager, ldo_agent, program_start_date):
    assert rewards_manager.available_allocations() == 0
    chain.sleep(floor(1.5 * rewards_period))
    chain.mine()
    assert rewards_manager.available_allocations() == rewards_limit
    rewards_manager.pause({"from": ldo_agent})
    assert rewards_manager.available_allocations() == rewards_limit
    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.available_allocations() == rewards_limit

    rewards_manager.unpause(program_start_date + 2 * rewards_period, rewards_limit, {"from": ldo_agent})
    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.available_allocations() == 2 * rewards_limit


def test_allocations_limit_calculation_with_changed_rewards_limit(rewards_manager, ldo_agent):
    assert rewards_manager.available_allocations() == 0
    chain.sleep(floor(1.5 * rewards_period))
    chain.mine()
    assert rewards_manager.available_allocations() == rewards_limit

    rewards_manager.set_rewards_limit_per_period(2 * rewards_limit, {"from": ldo_agent})
    assert rewards_manager.available_allocations() == rewards_limit
    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.available_allocations() == rewards_limit + 2 * rewards_limit

    rewards_manager.set_rewards_limit_per_period(0.5 * rewards_limit, {"from": ldo_agent})
    assert rewards_manager.available_allocations() == rewards_limit + 2 * rewards_limit
    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.available_allocations() == rewards_limit + 2 * rewards_limit + 0.5 * rewards_limit


def test_set_rewards_limit_per_period(rewards_manager, ldo_agent, stranger, helpers):
    assert rewards_manager.rewards_limit_per_period() == rewards_limit

    assert rewards_manager.available_allocations() == 0
    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.available_allocations() == rewards_limit

    with reverts():
        rewards_manager.set_rewards_limit_per_period(2 * rewards_limit, {"from": stranger})

    tx = rewards_manager.set_rewards_limit_per_period(2 * rewards_limit, {"from": ldo_agent})
    assert rewards_manager.rewards_limit_per_period() == 2 * rewards_limit
    helpers.assert_single_event_named("RewardsLimitChanged", tx, {"new_limit": 2 * rewards_limit})

    assert rewards_manager.available_allocations() == rewards_limit
    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.available_allocations() == (1 + 2) * rewards_limit


def test_set_rewards_limit_per_period_when_paused(rewards_manager, ldo_agent, program_start_date):
    assert rewards_manager.rewards_limit_per_period() == rewards_limit

    assert rewards_manager.available_allocations() == 0
    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.available_allocations() == rewards_limit

    rewards_manager.pause({"from": ldo_agent})

    chain.sleep(2 * rewards_period)
    chain.mine()

    rewards_manager.set_rewards_limit_per_period(2 * rewards_limit, {"from": ldo_agent})
    assert rewards_manager.rewards_limit_per_period() == 2 * rewards_limit

    rewards_manager.unpause(program_start_date + 3 * rewards_period, rewards_limit, {"from": ldo_agent})

    assert rewards_manager.available_allocations() == rewards_limit
    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.available_allocations() == (1 + 2) * rewards_limit


def test_pause(rewards_manager, ldo_agent, stranger, helpers, balancer_allocator, program_start_date):
    assert rewards_manager.is_paused() == False

    rewards_manager.seed_allocations(0, '', 0, {"from": balancer_allocator})

    with reverts():
        rewards_manager.pause({"from": stranger})

    tx = rewards_manager.pause({"from": ldo_agent})
    helpers.assert_single_event_named("Paused", tx, {"actor": ldo_agent})
    assert rewards_manager.is_paused() == True

    assert rewards_manager.available_allocations() == 0

    with reverts():
        rewards_manager.seed_allocations(0, '', 0, {"from": balancer_allocator})

    with reverts():
        rewards_manager.unpause(program_start_date, 0, {"from": stranger})

    tx = rewards_manager.unpause(program_start_date, 0, {"from": ldo_agent})
    helpers.assert_single_event_named("Unpaused", tx, {"actor": ldo_agent})
    assert rewards_manager.is_paused() == False

    rewards_manager.seed_allocations(0, '', 0, {"from": balancer_allocator})


def test_set_allocations_limit(rewards_manager, ldo_agent, stranger, helpers):
    assert rewards_manager.available_allocations() == 0

    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.available_allocations() == rewards_limit

    with reverts():
        rewards_manager.set_allocations_limit(10, {"from": stranger})

    tx = rewards_manager.set_allocations_limit( 10, {"from": ldo_agent})
    helpers.assert_single_event_named(
        "AllocationsLimitChanged", 
        tx, 
        {"new_limit": 10}
    )
    assert rewards_manager.available_allocations() == 10


def test_seed_allocations(
    rewards_manager,
    ldo_agent,
    ldo_token,
    stranger,
    helpers,
    dao_treasury,
    balancer_allocator,
    program_start_date
):
    with reverts():
        rewards_manager.seed_allocations(0, '', 0, {"from": stranger})

    rewards_manager.pause({"from": ldo_agent})
    with reverts():
        rewards_manager.seed_allocations(0, '', 0, {"from": balancer_allocator})
    rewards_manager.unpause(program_start_date, 0, {"from": ldo_agent})


    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.available_allocations() == rewards_limit

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
    assert rewards_manager.available_allocations() == 0
    assert ldo_token.balanceOf(rewards_manager) == 5000 * 10**18
    assert ldo_token.balanceOf(MERKLE_CONTRACT) == rewards_limit


def test_recover_erc20(rewards_manager, ldo_agent, ldo_token, stranger, helpers, dao_treasury):
    ldo_token.transfer(rewards_manager, 100, {"from": dao_treasury})
    assert ldo_token.balanceOf(rewards_manager) == 100

    with reverts('manager: not permitted'):
        rewards_manager.recover_erc20(ldo_token, 100, ldo_agent, {"from": stranger})

    balance = ldo_token.balanceOf(ldo_agent)

    tx = rewards_manager.recover_erc20(ldo_token, 100, ldo_agent, {"from": ldo_agent})
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
    helpers
):
    assert ldo_token.balanceOf(rewards_manager) == 0

    with reverts('manager: not permitted'):
        rewards_manager.recover_erc20(ldo_token, 100, ldo_agent, {"from": stranger})
    with reverts('manager: token transfer failed'):
        rewards_manager.recover_erc20(ldo_token, 100, ldo_agent, {"from": ldo_agent})
