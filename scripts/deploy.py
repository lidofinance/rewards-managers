import sys
import time
from brownie import RewardsManager
from utils.config import (
    ldo_token_address,
    get_is_live,
    get_deployer_account,
    prompt_bool,
    get_env
)


def deploy_manager(owner, allocator, start_date, tx_params):
    # Etherscan doesn't support Vyper verification yet
    return RewardsManager.deploy(
        owner, # _owner
        allocator, # _allocator
        start_date, # _start_date
        tx_params,
        publish_source=False,
    )

def main():
    is_live = get_is_live()
    deployer = get_deployer_account(is_live)
    allocator = get_env('ALLOCATOR')
    owner = get_env('OWNER')
    start_date = get_env('START_DATE')

    print('Deployer:', deployer)
    print('Allocator:', allocator)
    print('Owner:', owner)
    print(
        'Program start date:', 
        time.ctime(int(start_date))
    )

    sys.stdout.write('Proceed? [y/n]: ')

    if not prompt_bool():
        print('Aborting')
        return

    deploy_manager(
        owner,
        allocator,
        start_date,
        tx_params={"from": deployer}
    )
