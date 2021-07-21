import pytest
import time
from brownie import reverts, chain
from scripts.deploy import deploy_manager
from math import floor

rewards_limit = 25 * 1000 * 10**18
rewards_period = 3600 * 24 * 7
start_date = 1627257600 # Mon Jul 26 2021 00:00:00 GMT+0000

def test_start_program(interface, deployer, ldo_agent, balancer_allocator, ):
    amount = 100000 * 10**18

    manager_contract = deploy_manager(ldo_agent, balancer_allocator, start_date, {"from": deployer})

    assert manager_contract.available_allocations() == 0

    chain.sleep(start_date - chain.time() - 1 ) # 1 second before program start date
    chain.mine()

    assert manager_contract.available_allocations() == 0

    chain.sleep(1) # program start date
    chain.mine()

    assert manager_contract.available_allocations() == rewards_limit





    
