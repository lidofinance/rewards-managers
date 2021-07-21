import pytest
import time
from brownie import reverts, chain
from scripts.deploy import deploy_manager
from math import floor

rewards_limit = 25 * 1000 * 10**18
rewards_period = 3600 * 24 * 7
start_date = 1627257600 # Mon Jul 26 2021 00:00:00 GMT+0000

def test_start_program(interface, deployer, ldo_agent, balancer_allocator, ldo_token):
    amount = 100000 * 10**18

    manager_contract = deploy_manager(ldo_agent, balancer_allocator, start_date, {"from": deployer})
    merkle_owner = interface.MerkleRedeem('0x6bd0B17713aaa29A2d7c9A39dDc120114f9fD809').owner()
    if merkle_owner != manager_contract:
        interface.MerkleRedeem('0x6bd0B17713aaa29A2d7c9A39dDc120114f9fD809')\
            .transferOwnership(manager_contract, {"from": merkle_owner})


    assert manager_contract.available_allocations() == 0
    
    ldo_token.transfer(manager_contract, amount, {"from": ldo_agent})
    assert ldo_token.balanceOf(manager_contract) == amount

    chain.sleep(start_date - chain.time() - 1 ) # 1 second before program start date
    chain.mine()

    with reverts('manager: not enought amount approved'):
        manager_contract.seed_allocations(0, '', rewards_limit, {"from": balancer_allocator})

    assert manager_contract.available_allocations() == 0

    chain.sleep(1) # program start date
    chain.mine()

    with reverts('manager: not enought amount approved'):
        manager_contract.seed_allocations(0, '', rewards_limit + 1, {"from": balancer_allocator})
    
    assert manager_contract.available_allocations() == rewards_limit
    manager_contract.seed_allocations(0, '', rewards_limit, {"from": balancer_allocator})
    assert ldo_token.balanceOf(manager_contract) == amount - rewards_limit
    assert manager_contract.available_allocations() == 0

    chain.sleep(rewards_period) # waiting for next period
    chain.mine()
    
    assert manager_contract.available_allocations() == rewards_limit





    
