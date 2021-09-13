import pytest
from brownie import reverts, chain
from math import floor

rewards_limit = 25 * 1000 * 10**18
rewards_period = 3600 * 24 * 7

@pytest.mark.parametrize(
    'period', 
    [   
        rewards_period,
        floor(0.5*rewards_period), 
        4*rewards_period , 
        4*rewards_period + 1, 
        4*rewards_period - 1,
        5*rewards_period
    ]
)
def test_out_of_funding_date(rewards_manager, period, ldo_token, dao_treasury, program_start_date):
    amount = 100000 * 10**18
    
    ldo_token.transfer(rewards_manager, amount, {"from": dao_treasury})
    assert ldo_token.balanceOf(rewards_manager) == amount

    out_of_funding_date = program_start_date + rewards_period * 4

    chain.sleep(period)
    chain.mine()
    assert rewards_manager.out_of_funding_date() == out_of_funding_date
    assert rewards_manager.period_finish() == out_of_funding_date


def test_out_of_funding_date_with_limit_change(
    rewards_manager, 
    ldo_token, 
    dao_treasury,
    ldo_agent,
    program_start_date
):
    amount = 100000 * 10**18
    
    ldo_token.transfer(rewards_manager, amount, {"from": dao_treasury})
    assert ldo_token.balanceOf(rewards_manager) == amount

    out_of_funding_date = program_start_date + rewards_period * 4

    chain.sleep(rewards_period)
    chain.mine()
    assert rewards_manager.out_of_funding_date() == out_of_funding_date
    assert rewards_manager.period_finish() == out_of_funding_date
    assert rewards_manager.available_allocations() == rewards_limit
 
    out_of_funding_date = program_start_date + 2 * rewards_period

    rewards_manager.set_rewards_limit_per_period(2 * rewards_limit, {"from": ldo_agent})
    assert rewards_manager.rewards_limit_per_period() == 2 * rewards_limit
    assert rewards_manager.out_of_funding_date() == out_of_funding_date
    assert rewards_manager.period_finish() == out_of_funding_date
