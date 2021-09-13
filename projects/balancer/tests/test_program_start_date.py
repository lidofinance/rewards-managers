import pytest
import time
from brownie import reverts, chain
from scripts.deploy import deploy_manager
from math import floor

rewards_limit = 25 * 1000 * 10**18
rewards_period = 3600 * 24 * 7
start_date = 1629072000 # Mon Aug 16 2021 00:00:00 GMT+0000

def test_start_program(interface, deployer, ldo_agent, balancer_allocator, ldo_token):
    amount = 100000 * 10**18

    manager_contract = deploy_manager(balancer_allocator, start_date, {"from": deployer})
    manager_contract.transfer_ownership(ldo_agent, {"from": deployer})
    merkle_owner = interface.MerkleRedeem('0x884226c9f7b7205f607922E0431419276a64CF8f').owner()
    if merkle_owner != manager_contract:
        interface.MerkleRedeem('0x884226c9f7b7205f607922E0431419276a64CF8f')\
            .transferOwnership(manager_contract, {"from": merkle_owner})


    assert manager_contract.available_allocations() == rewards_limit
    
    ldo_token.transfer(manager_contract, amount, {"from": ldo_agent})
    assert ldo_token.balanceOf(manager_contract) == amount



    chain.sleep(start_date + rewards_period - chain.time() - 1 ) # 1 second before program start date
    chain.mine()

    with reverts('manager: not enought amount approved'):
        manager_contract.seed_allocations(0, '', 2*rewards_limit, {"from": balancer_allocator})

    assert manager_contract.available_allocations() == rewards_limit

    chain.sleep(10) # program start date
    chain.mine()

    with reverts('manager: not enought amount approved'):
        manager_contract.seed_allocations(0, '', 2 * rewards_limit + 1, {"from": balancer_allocator})
    
    assert manager_contract.available_allocations() == rewards_limit * 2
    manager_contract.seed_allocations(0, '', rewards_limit, {"from": balancer_allocator})
    assert ldo_token.balanceOf(manager_contract) == amount - rewards_limit
    assert manager_contract.available_allocations() == rewards_limit

    chain.sleep(rewards_period) # waiting for next period
    chain.mine()
    
    assert manager_contract.available_allocations() == rewards_limit * 2





    
