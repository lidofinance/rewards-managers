import pytest
from brownie import RewardsManager, reverts
from utils.config import ldo_token_address


def test_deploy(RewardsManager, accounts):
    # deploy the contract
    rew_man = RewardsManager.deploy({'from': accounts[0]})
    
    assert rew_man.owner() == accounts[0]


