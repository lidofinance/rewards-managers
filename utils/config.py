import os
import sys
from brownie import network, accounts


ldo_token_address = '0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32'
lido_dao_agent_address = '0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c'


def get_is_live():
    return network.show_active() != 'development'


def get_env(name, is_required=True, message=None, default=None):
    if name not in os.environ:
        if is_required:
            raise EnvironmentError(message or f'Please set {name} env variable')
        else:
            return default
    return os.environ[name]


def get_deployer_account(is_live):
    if is_live and 'DEPLOYER' not in os.environ:
        raise EnvironmentError(
            'Please set DEPLOYER env variable to the deployer account name')

    deployer = accounts.load(os.environ['DEPLOYER']) \
        if is_live or 'DEPLOYER' in  os.environ \
        else accounts[0]
    
    return deployer


def prompt_bool():
    choice = input().lower()
    if choice in {'yes', 'y'}:
       return True
    elif choice in {'no', 'n'}:
       return False
    else:
       sys.stdout.write("Please respond with 'yes' or 'no'")
