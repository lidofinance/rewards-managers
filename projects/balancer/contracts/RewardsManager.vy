# @version 0.2.12
# @author bulbozaur <alexandrtarelkin92@gmail.com>
# @notice A manager contract for the Balancer Merkle Rewards contract.

# @license MIT


interface ERC20:
    def allowance(arg0: address, arg1: address) -> uint256: view
    def balanceOf(arg0: address) -> uint256: view
    def approve(_spender: address, _value: uint256) -> bool: nonpayable
    def transfer(_to: address, _value: uint256) -> bool: nonpayable


interface IRewardsContract:
    def seedAllocations(_week: uint256, _merkleRoot: bytes32, _totalAllocation: uint256): nonpayable
    def transferOwnership(newOwner: address): nonpayable


event OwnerChanged:
    new_owner: indexed(address)


event AllocatorChanged:
    new_allocator: indexed(address)


event Allocation:
    amount: uint256


event RewardsLimitChanged:
    new_limit: uint256


event ERC20TokenRecovered:
    token: indexed(address)
    amount: uint256
    recipient: indexed(address)


event Paused:
    actor: indexed(address)


event Unpaused:
    actor: indexed(address)


event AllocationsLimitChanged:
    new_limit: uint256


event RewardContractOwnershipTransfered:
    new_owner: indexed(address)


owner: public(address)
allocator: public(address)

rewards_contract: constant(address) = 0x884226c9f7b7205f607922E0431419276a64CF8f
rewards_token: constant(address) = 0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32

allocations_limit: public(uint256)
rewards_limit_per_period: public(uint256)
rewards_period_duration: constant(uint256) = 604800  # 3600 * 24 * 7
last_accounted_period_start_date: public(uint256)

is_paused: public(bool)


@external
def __init__(
    _allocator: address,
    _start_date: uint256
):
    self.owner = msg.sender
    self.allocator = _allocator

    self.allocations_limit = 0
    self.is_paused = False

    self.rewards_limit_per_period = 25000 * 10**18
    self.last_accounted_period_start_date = _start_date - rewards_period_duration

    log OwnerChanged(self.owner)
    log AllocatorChanged(self.allocator)
    log AllocationsLimitChanged(self.allocations_limit)
    log Unpaused(self.owner)
    log RewardsLimitChanged(self.rewards_limit_per_period)


@internal
@view
def _unaccounted_periods() -> uint256:
    last_accounted_period_start_date: uint256 = self.last_accounted_period_start_date
    if (last_accounted_period_start_date > block.timestamp):
        return 0
    return (block.timestamp - self.last_accounted_period_start_date) / rewards_period_duration


@internal
def _update_last_accounted_period_start_date():
    """
    @notice 
        Updates last_accounted_period_start_date to timestamp of current period
    """
    self.last_accounted_period_start_date = self.last_accounted_period_start_date \
        + rewards_period_duration * self._unaccounted_periods()


@internal
@view
def _available_allocations() -> uint256:
    if self.is_paused == True:
        return self.allocations_limit

    return self.allocations_limit + self._unaccounted_periods() * self.rewards_limit_per_period


@external
@view
def available_allocations() -> uint256:
    """
    @notice 
        Returns current allocations limit for Merkle Rewards contract 
        as sum of merkle contract accounted limit
        and calculated allocations amount for unaccounted period 
        since last allocations limit update
    """
    return self._available_allocations()


@internal
def _set_allocations_limit(_new_allocations_limit: uint256):
    """
    @notice Changes the allocations limit for Merkle Rewadrds contact. 
    """
    self.allocations_limit = _new_allocations_limit

    # Reseting unaccounted period date
    self._update_last_accounted_period_start_date()
    
    log AllocationsLimitChanged(_new_allocations_limit)


@internal
def _update_allocations_limit():
    """
    @notice Updates allowance based on current calculated allocations limit
    """
    new_allocations_limit: uint256 = self._available_allocations()
    self._set_allocations_limit(new_allocations_limit)


@external
def set_allocations_limit(_new_allocations_limit: uint256):
    """
    @notice Changes the allocations limit for Merkle Rewadrds contact. Can only be called by owner.
    """
    assert msg.sender == self.owner, "manager: not permitted"
    self._set_allocations_limit(_new_allocations_limit)


@external
def set_rewards_limit_per_period(_new_limit: uint256):
    """
    @notice 
        Updates all finished periods since last allowance update
        and changes the amount of available allocations increasing
        per reward period.
        Can only be called by the current owner.
    """
    assert msg.sender == self.owner, "manager: not permitted"

    self._update_allocations_limit()
    self.rewards_limit_per_period = _new_limit
    
    log RewardsLimitChanged(self.rewards_limit_per_period)


@external
def seed_allocations(_week: uint256, _merkle_root: bytes32, _amount: uint256):
    """
    @notice
        Wraps seedAllocations(_week: uint256, _merkle_root: bytes32, _amount: uint256)
        of Merkle rewards contract with amount limited by available_allocations()
    """
    assert msg.sender == self.allocator, "manager: not permitted"
    assert self.is_paused == False, "manager: contract is paused"

    assert ERC20(rewards_token).balanceOf(self) >= _amount, "manager: reward token balance is low"

    available_allocations: uint256 = self._available_allocations()
    assert available_allocations >= _amount, "manager: not enought amount approved"

    ERC20(rewards_token).approve(rewards_contract, _amount)
    self._set_allocations_limit(available_allocations - _amount)

    IRewardsContract(rewards_contract).seedAllocations(_week, _merkle_root, _amount)

    log Allocation(_amount)


@external
def pause():
    """
    @notice
        Pause allocations increasing and rejects seedAllocations calling
    """
    assert msg.sender == self.owner, "manager: not permitted"
    
    self._update_allocations_limit()
    self.is_paused = True

    log Paused(msg.sender)


@external
def unpause(_start_date: uint256, _new_allocations_limit: uint256):
    """
    @notice
        Unpause allocations increasing and allows seedAllocations calling
    """
    assert msg.sender == self.owner, "manager: not permitted"
    
    self._set_allocations_limit(_new_allocations_limit)
    self.last_accounted_period_start_date = _start_date - rewards_period_duration
    self.is_paused = False

    log Unpaused(msg.sender)


@internal
@view
def _out_of_funding_date() -> uint256:
    """
    @notice 
        Expected date of the manager to run out of funds at the current rate. 
        All the allocated funds would be allowed for spending by Merkle Reward contract.
    """
    rewards_balance: uint256 = ERC20(rewards_token).balanceOf(self)
    accounted_allocations_limit: uint256 = self.allocations_limit

    # Handling accounted_allocations_limit and rewards_balance diff underflow exception
    if (rewards_balance < accounted_allocations_limit):
        unaccounted_periods: uint256 = (accounted_allocations_limit - rewards_balance) / self.rewards_limit_per_period
        # incrementing unaccounted periods count to get the end of last period instead of the begining
        unaccounted_periods += 1
        return self.last_accounted_period_start_date - unaccounted_periods * rewards_period_duration
    
    unaccounted_periods: uint256 = (rewards_balance - accounted_allocations_limit) / self.rewards_limit_per_period
    # incrementing unaccounted periods count to get the end of last period instead of the begining
    unaccounted_periods += 1
    return self.last_accounted_period_start_date + unaccounted_periods * rewards_period_duration


@external
@view
def out_of_funding_date() -> uint256:
    return self._out_of_funding_date()


@external
@view
def period_finish() -> uint256:
    return self._out_of_funding_date()


@external
def transfer_ownership(_to: address):
    """
    @notice Changes the contract owner. Can only be called by the current owner.
    """
    assert msg.sender == self.owner, "manager: not permitted"
    self.owner = _to
    log OwnerChanged(self.owner)


@external
def set_allocator(_new_allocator: address):
    """
    @notice Changes the allocator. Can only be called by the current owner.
    """
    assert msg.sender == self.owner, "manager: not permitted"
    self.allocator = _new_allocator
    log AllocatorChanged(self.allocator)


@external
def transfer_rewards_contract_ownership(_new_owner: address):
    """
    @notice Changes the owner of reward contract. Can only be called by the current owner.
    """
    assert msg.sender == self.owner, "manager: not permitted"
    IRewardsContract(rewards_contract).transferOwnership(_new_owner)

    log RewardContractOwnershipTransfered(_new_owner)


@external
def recover_erc20(_token: address, _amount: uint256, _recipient: address = msg.sender):
    """
    @notice
        Transfers specified amount of the given ERC20 token from self
        to the recipient. Can only be called by the owner.
    """
    assert msg.sender == self.owner, "manager: not permitted"

    if _amount > 0:
        assert ERC20(_token).transfer(_recipient, _amount), "manager: token transfer failed"
        log ERC20TokenRecovered(_token, _amount, _recipient)
