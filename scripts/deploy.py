import sys

from brownie import RewardsManager, Wei

from utils.config import (
    farming_rewards_address,
    lido_dao_agent_address,
    gas_price,
    get_is_live,
    get_deployer_account,
    prompt_bool
)


def deploy_manager(tx_params, publish_source):
    # Etherscan doesn't support Vyper verification yet
    manager = RewardsManager.deploy(farming_rewards_address, tx_params, publish_source=publish_source)

    assert manager.rewards_contract() == farming_rewards_address

    manager.transfer_ownership(lido_dao_agent_address, tx_params)

    assert manager.owner() == lido_dao_agent_address

    return manager


def main():
    is_live = get_is_live()
    deployer = get_deployer_account(is_live)

    print('Deployer:', deployer)
    print('Reward farming address:', farming_rewards_address)
    print('Gas price:', gas_price)

    sys.stdout.write('Proceed? [y/n]: ')

    if not prompt_bool():
        print('Aborting')
        return

    deploy_manager(
        tx_params={"from": deployer, "gas_price": Wei(gas_price), "required_confs": 1},
        publish_source=is_live
    )
