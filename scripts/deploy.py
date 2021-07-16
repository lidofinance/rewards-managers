import sys

from brownie import RewardsManager

from utils.config import (
    ldo_token_address,
    get_is_live,
    get_deployer_account,
    prompt_bool,
    get_env
)


def deploy_manager(owner, allocator, merkle_contract, tx_params):
    # Etherscan doesn't support Vyper verification yet
    return RewardsManager.deploy(
        owner, # _owner
        allocator, # _allocator
        merkle_contract, # _rewards_contract
        tx_params,
        publish_source=False,
    )

def main():
    is_live = get_is_live()
    deployer = get_deployer_account(is_live)
    allocator = get_env('ALLOCATOR')
    merkle_contract = get_env('MERKLE_CONTRACT')
    owner = get_env('OWNER')

    print('Deployer:', deployer)
    print('Allocator:', allocator)
    print('Merkle contract', merkle_contract)
    print('LDO token address:', ldo_token_address)
    print('Owner:', owner)

    sys.stdout.write('Proceed? [y/n]: ')

    if not prompt_bool():
        print('Aborting')
        return

    deploy_manager(
        owner,
        allocator,
        merkle_contract,
        tx_params={"from": deployer}
    )
