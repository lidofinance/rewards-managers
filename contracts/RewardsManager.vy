# @version 0.2.15
# @notice A manager contract for the FarmingRewards contract.
# @license MIT
from vyper.interfaces import ERC20

interface FarmingRewards:
    def tokenRewards(index: uint256) -> (address, uint256, uint256, address, uint256, uint256, uint256, uint256): view
    def notifyRewardAmount(index: uint256, reward: uint256): nonpayable

owner: public(address)
gift_index: public(uint256)
rewards_contract: public(address)
ldo_token: constant(address) = 0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32

@external
def __init__():
    self.owner = msg.sender

@external
def transfer_ownership(_to: address):
    """
    @notice
        Changes the contract owner.
        Can only be called by the current owner.
    """
    assert msg.sender == self.owner, "not permitted"
    self.owner = _to

@external
def set_rewards_contract(_rewards_contract: address):
    """
    @notice
        Sets the FarmingRewards contract.
        Can only be called by the owner.
    """
    assert msg.sender == self.owner, "not permitted"
    self.rewards_contract = _rewards_contract

@external
def set_gift_index(_gift_index: uint256):
    """
    @notice
        Sets the gift index in FarmingRewards contract.
        Can only be called by the owner.
    """
    assert msg.sender == self.owner, "not permitted"
    self.gift_index = _gift_index

@view
@internal
def _period_finish(rewards_contract: address, gift_index: uint256) -> uint256:
    # TODO: figure out if there is a more proper readable way to do this
    gift_token: address = ZERO_ADDRESS
    scale: uint256 = 0
    duration: uint256 = 0
    reward_distribution: address = ZERO_ADDRESS
    period_finish: uint256 = 0
    reward_rate: uint256 = 0
    last_update_time: uint256 = 0
    reward_per_token_stored: uint256 = 0

    gift_token, scale, duration, reward_distribution, period_finish, reward_rate, last_update_time, reward_per_token_stored = FarmingRewards(rewards_contract).tokenRewards(gift_index)

    return period_finish

@view
@internal
def _is_rewards_period_finished(rewards_contract: address, gift_index: uint256) -> bool:
    return block.timestamp >= self._period_finish(rewards_contract, gift_index)

@view
@external
def is_rewards_period_finished() -> bool:
    """
    @notice Whether the current rewards period has finished.
    """
    return self._is_rewards_period_finished(self.rewards_contract, self.gift_index)

@view
@external
def out_of_funding_date() -> uint256:
    return self._period_finish(self.rewards_contract, self.gift_index)

@external
def start_next_rewards_period():
    """
    @notice
        Starts the next rewards via calling `FarmingRewards.notifyRewardAmount()`
        and transferring `ldo_token.balanceOf(self)` tokens to `FarmingRewards`.
        The `FarmingRewards` contract handles all the rest on its own.
        The current rewards period must be finished by this time.
    """
    rewards: address = self.rewards_contract
    gift_index: uint256 = self.gift_index
    amount: uint256 = ERC20(ldo_token).balanceOf(self)

    assert rewards != ZERO_ADDRESS and amount != 0, "manager: rewards disabled"
    assert self._is_rewards_period_finished(rewards, gift_index), "manager: rewards period not finished"

    assert ERC20(ldo_token).transfer(rewards, amount), "manager: unable to transfer reward tokens"

    FarmingRewards(rewards).notifyRewardAmount(gift_index, amount)

@external
def recover_erc20(_token: address, _amount: uint256, _recipient: address = msg.sender):
    """
    @notice
        Transfers the given _amount of the given ERC20 token from self
        to the _recipient. Can only be called by the owner.
    """
    assert msg.sender == self.owner, "not permitted"

    if _amount != 0:
        assert ERC20(_token).transfer(_recipient, _amount), "token transfer failed"
