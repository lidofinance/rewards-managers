import pytest

@pytest.fixture
def rewards_manager_contract(RewardsManager, accounts):
    # deploy the contract
    yield RewardsManager.deploy({'from': accounts[0]});

def test_ownership(rewards_manager_contract, accounts):
    assert rewards_manager_contract.owner() == accounts[0];
