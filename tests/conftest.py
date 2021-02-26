import pytest

@pytest.fixture(scope='module')
def stranger(accounts):
    return accounts[0]

@pytest.fixture(scope='module')
def arcx_deployer(accounts):
    return accounts[1]

@pytest.fixture(scope='module')
def lido_rewards_manager_deployer(accounts):
    return accounts[2]

@pytest.fixture(scope='module')
def ldo_token_address():
    return '0x5a98fcbea516cf06857215779fd812ca3bef1b32'

@pytest.fixture(scope='module')
def lido_dao_agent_address():
    return '0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c'

@pytest.fixture(scope='module')
def ldo_token(interface, ldo_token_address):
    return interface.ERC20(ldo_token_address)


@pytest.fixture(scope='module')
def staking_token(interface):
    # 3pool LP token
    return interface.ERC20('0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490')

@pytest.fixture(scope='module')
def staking_token_whale(accounts):
    return accounts.at('0x890f4e345b1daed0367a877a1612f86a1f86985f', {'force': True})

@pytest.fixture(scope='function')
def rewards_manager(RewardsManager, lido_rewards_manager_deployer):
    return RewardsManager.deploy({"from": lido_rewards_manager_deployer})

@pytest.fixture(scope='function')
def joint_campaign(JointCampaignMock, arcx_deployer, rewards_manager, ldo_token_address, staking_token):
    contract = JointCampaignMock.deploy({"from": arcx_deployer})
    arc_dao_address = '0x1DEBBC50322150EB44DE3b663d5faA89c12b07ff'
    arcx_token_address = '0xED30Dd7E50EdF3581AD970eFC5D9379Ce2614AdB'
    mozart_address = '0x0BCb3b8BeCaae10Acc13FDDc0aB09be3351Cd30d'
    contract.init(arc_dao_address, arcx_deployer, rewards_manager.address, arcx_token_address, ldo_token_address, staking_token.address, [10000000000], [10000000000], 200, mozart_address, {"from": arcx_deployer})
    return contract
