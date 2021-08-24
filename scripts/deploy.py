import sys

from brownie import (
    network,
    accounts,
    RewardsManager,
    MooniswapFactoryGovernance,
    Mooniswap,
    FarmingRewards,
    Wei,
    ZERO_ADDRESS
)

from utils.config import (
    lp_token_address,
    ldo_token_address,
    lido_dao_agent_address,
    steth_token_address,
    dai_address,
    one_inch_token_address,
    initial_rewards_duration_sec,
    gas_price,
    rewards_amount,
    scale,
    get_is_live,
    get_deployer_account,
    prompt_bool
)


def deploy_manager(tx_params):
    # Etherscan doesn't support Vyper verification yet
    return RewardsManager.deploy(tx_params, publish_source=False)


def deploy_mooniswap_factory(mothership, tx_params, publish_source=True):
    return MooniswapFactoryGovernance.deploy(mothership, tx_params, publish_source=publish_source)


def deploy_mooniswap(name, symbol, mooniswap_factory, tx_params, publish_source=True):
    return Mooniswap.deploy(
        steth_token_address, # _token0
        dai_address, # _token1
        name, # name
        symbol, # symbol
        mooniswap_factory, # _mooniswapFactoryGovernance
        tx_params, 
        publish_source=publish_source
    )


def deploy_rewards(mooniswap, rewards_amount, rewards_manager, scale, tx_params, publish_source=True):
    return FarmingRewards.deploy(
        mooniswap, # Mooniswap
        one_inch_token_address, # _gift
        rewards_amount, # _duration
        rewards_manager, # _rewardDistribution
        scale, # scale
        tx_params,
        publish_source=publish_source
    )


def deploy_manager_and_rewards(tx_params, publish_source=True):
    manager = deploy_manager(tx_params)

    mooniswap_factory = deploy_mooniswap_factory(ZERO_ADDRESS, tx_params=tx_params, publish_source=publish_source)

    mooniswap = deploy_mooniswap("stETH-DAI Liquidity Pool Token", "LP", mooniswap_factory, tx_params, publish_source=publish_source)

    rewards = FarmingRewards.deploy(
        mooniswap, 
        one_inch_token_address, 
        rewards_amount, 
        manager, 
        scale, 
        tx_params,
        publish_source=publish_source
    )

    rewards.addGift(ldo_token_address, rewards_amount, manager, scale, tx_params)

    manager.set_rewards_contract(rewards, tx_params)
    assert manager.rewards_contract() == rewards
    
    manager.set_gift_index(1, tx_params)
    assert manager.gift_index() == 1
    
    manager.transfer_ownership(lido_dao_agent_address, tx_params)

    return (manager, rewards)


def main():
    is_live = get_is_live()
    deployer = get_deployer_account(is_live)

    print('Deployer:', deployer)
    print('Initial rewards duration:', initial_rewards_duration_sec)
    print('LP token address:', lp_token_address)
    print('LDO token address:', ldo_token_address)
    print('Gas price:', gas_price)

    sys.stdout.write('Proceed? [y/n]: ')

    if not prompt_bool():
        print('Aborting')
        return

    deploy_manager_and_rewards(
        rewards_duration=initial_rewards_duration_sec,
        tx_params={"from": deployer, "gas_price": Wei(gas_price), "required_confs": 1},
        publish_source=is_live
    )
