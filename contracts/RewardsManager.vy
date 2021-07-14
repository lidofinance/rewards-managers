# @version 0.2.12
# @notice A manager contract for the StakingRewards contract.
# @author skozin
# @license MIT
from vyper.interfaces import ERC20


event OwnerChanged:
    new_owner: address


event AllocatorChanged:
    new_allocator: address


event Allocation:
    amount: uint256


event RewardsLimitChanged:
    new_limit: uint256


event ERC20TokenRecovered:
    token: address
    amount: uint256
    recipient: address


event Paused:
    actor: address


event Unpaused:
    actor: address


interface IRewardsContract:
    def seedAllocations(_week: uint256, _merkleRoot: bytes32, _totalAllocation: uint256): nonpayable


owner: public(address)
allocator: public(address)

rewards_contract: public(address)
rewards_token: public(address)

rewards_limit_per_period: public(uint256)
rewards_period_duration: constant(uint256) = 604800  # 3600 * 24 * 7
last_allowance_period_date: public(uint256)


@external
def __init__(
    _owner: address,
    _allocator: address,
    _rewards_token: address,
    _rewards_contract: address,
    _rewards_limit_per_period: uint256
):
    self.owner = _owner
    self.allocator = _allocator
    self.rewards_limit_per_period = _rewards_limit_per_period
    self.rewards_token = _rewards_token
    self.rewards_contract = _rewards_contract

    self.last_allowance_period_date = block.timestamp

    log OwnerChanged(self.owner)
    log AllocatorChanged(self.allocator)


@external
def transfer_ownership(_to: address):
    """
    @notice Changes the contract owner. Can only be called by the current owner.
    """
    assert msg.sender == self.owner, "manager: not permitted"
    self.owner = _to
    log OwnerChanged(self.owner)


@external
def change_allocator(_new_allocator: address):
    """
    @notice Changes the allocator. Can only be called by the current owner.
    """
    assert msg.sender == self.owner, "manager: not permitted"
    self.allocator = _new_allocator
    log AllocatorChanged(self.allocator)


@view
@internal
def _allowance() -> uint256:
    current_allowance: uint256 = ERC20(self.rewards_token).allowance(self, self.rewards_contract)
    scheduled_periods: uint256 = (block.timestamp - self.last_allowance_period_date) / rewards_period_duration
    return current_allowance + scheduled_periods * self.rewards_limit_per_period


@view
@external
def allowance() -> uint256:
    """
    @notice Returns current allowance for Rewards contract
    """
    return self._allowance()


@view
@internal
def _is_rewards_period_finished() -> bool:
    avalable_balance: uint256 = ERC20(self.rewards_token).balanceOf(self) - self._allowance()
    
    return block.timestamp >= self.last_allowance_period_date + rewards_period_duration * (avalable_balance / self.rewards_limit_per_period)


@view
@external
def is_rewards_period_finished() -> bool:
    """
    @notice Whether the current rewards period has finished.
    """
    return self._is_rewards_period_finished()


@internal
def _updateAlowance():
    """
    @notice Updates allowance based on 
    """
    ERC20(self.rewards_token).approve(self.rewards_contract, self._allowance())
    self.last_allowance_period_date = self.last_allowance_period_date + rewards_period_duration


@external
def seedAllocations(_week: uint256, _merkle_root: bytes32, _amount: uint256):
    """
    @notice
        Allocates ldo for merkle reward contract with seed root and week number
        Can only be called by the allocator
    """
    assert msg.sender == self.allocator, "manager: not permitted"

    rewards_token: address = self.rewards_token

    self._updateAlowance()

    assert ERC20(rewards_token).balanceOf(self) >= _amount, "manager: reward token balance is low"
    assert ERC20(rewards_token).allowance(self, self.rewards_contract) >= _amount, "manager: not enought amount approved"   

    IRewardsContract(self.rewards_contract).seedAllocations(_week, _merkle_root, _amount)

    log Allocation(_amount)


@external
def change_rewards_limit(_new_limit: uint256):
    """
    @notice Changes the rewards limit. Can only be called by the current owner.
    """
    assert msg.sender == self.owner, "manager: not permitted"
    self._updateAlowance()
    self.rewards_limit_per_period = _new_limit
    log RewardsLimitChanged(self.rewards_limit_per_period)


@external
def recover_erc20(_token: address, _recipient: address = msg.sender):
    """
    @notice
        Transfers the whole balance of the given ERC20 token from self
        to the recipient. Can only be called by the owner.
    """
    assert msg.sender == self.owner, "manager: not permitted"
    token_balance: uint256 = ERC20(_token).balanceOf(self)
    if token_balance != 0:
        assert ERC20(_token).transfer(_recipient, token_balance), "manager: token transfer failed"

    log ERC20TokenRecovered(_token, token_balance, _recipient)
