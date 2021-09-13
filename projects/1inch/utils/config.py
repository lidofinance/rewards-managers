import os
import sys
from brownie import network, accounts
from brownie.convert.datatypes import Wei

ldo_token_address = "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32"
dai_address = "0x6b175474e89094c44da98b954eedeac495271d0f"
steth_token_address = "0xae7ab96520de3a18e5e111b5eaab095312d7fe84"
one_inch_token_address = "0x111111111117dc0aa78b770fa6a738034120c302"
one_inch_token_owner = "0x5E89f8d81C74E311458277EA1Be3d3247c7cd7D1"
lido_dao_agent_address = "0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c"
lido_dao_voting_address = "0x2e59A20f205bB85a89C53f1936454680651E618e"
farming_rewards_address = "0xd7012cDeBF10d5B352c601563aA3A8D1795A3F52"
farming_rewards_owner = one_inch_token_owner
mooniswap_address = "0xC1A900Ae76dB21dC5aa8E418Ac0F4E888A4C7431"

gift_index = 1
gas_price = "90 gwei"
rewards_amount = Wei("200000 ether")
scale = Wei("1000000000000000000")
initial_rewards_duration_sec = 60 * 60 * 24 * 30 # one month


def get_is_live():
    return network.show_active() != "development"


def get_deployer_account(is_live):
    if is_live and "DEPLOYER" not in os.environ:
        raise EnvironmentError(
            "Please set DEPLOYER env variable to the deployer account name"
        )

    return accounts.load(os.environ["DEPLOYER"]) if is_live else accounts[0]


def get_env(name, is_required=True, message=None, default=None):
    if name not in os.environ:
        if is_required:
            raise EnvironmentError(message or f'Please set {name} env variable')
        else:
            return default
    return os.environ[name]


def prompt_bool():
    choice = input().lower()

    if choice in {"yes", "y"}:
        return True

    if choice in {"no", "n"}:
        return False

    sys.stdout.write("Please respond with 'yes' or 'no'")
