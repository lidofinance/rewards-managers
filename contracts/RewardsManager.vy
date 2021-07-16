# @version 0.2.12
# @author https://github.com/bulbozaur
# @notice A manager contract for the Merkle contract.

# @license MIT


interface ERC20:
    def allowance(arg0: address, arg1: address) -> uint256: view
    def balanceOf(arg0: address) -> uint256: view
    def approve(_spender: address, _value: uint256) -> bool: nonpayable
    def transfer(_to: address, _value: uint256) -> bool: nonpayable


interface IRewardsContract:
    def seedAllocations(_week: uint256, _merkleRoot: bytes32, _totalAllocation: uint256): nonpayable


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


event AllowanceChanged:
    spender: address
    new_allowance: uint256


owner: public(address)
allocator: public(address)

rewards_contract: public(address)
rewards_token: constant(address) = 0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32

rewards_limit_per_period: public(uint256)
rewards_period_duration: constant(uint256) = 604800  # 3600 * 24 * 7
last_allowance_period_date: public(uint256)

is_paused: public(bool)


@external
def __init__(
    _owner: address,
    _allocator: address,
    _rewards_contract: address
):
    self.owner = _owner
    self.allocator = _allocator
    self.rewards_contract = _rewards_contract

    self.rewards_limit_per_period = 25000 * 10**18
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
    current_allowance: uint256 = ERC20(rewards_token).allowance(self, self.rewards_contract)
    if self.is_paused == True:
        return current_allowance
    scheduled_periods: uint256 = (block.timestamp - self.last_allowance_period_date) / rewards_period_duration
    return current_allowance + scheduled_periods * self.rewards_limit_per_period


@view
@external
def allowance() -> uint256:
    """
    @notice 
        Returns current allowance for Rewards contract as sum of
        merkle contract allowance and allowance for period since
        last allowance update
    """
    return self._allowance()


@internal
def _update_last_allowance_period_date():
    periods: uint256 = ( block.timestamp - self.last_allowance_period_date ) / rewards_period_duration
    self.last_allowance_period_date = self.last_allowance_period_date + rewards_period_duration * periods


@internal
def _update_allowance():
    """
    @notice Updates allowance based on current callulated value
    """
    new_allowance: uint256 = self._allowance()
    ERC20(rewards_token).approve(self.rewards_contract, 0)
    ERC20(rewards_token).approve(self.rewards_contract, new_allowance)
    self._update_last_allowance_period_date()
    
    log AllowanceChanged(self.rewards_contract, new_allowance)


@external
def change_allowance( _spender: address, _new_allowance: uint256):
    """
    @notice Changes the allowance of reward contract. Can only be callded by owner.
    """
    assert msg.sender == self.owner, "manager: not permitted"
    if _spender == self.rewards_contract:
        self._update_last_allowance_period_date()
    ERC20(rewards_token).approve(self.rewards_contract, 0)
    ERC20(rewards_token).approve(self.rewards_contract, _new_allowance)
    
    log AllowanceChanged(_spender, _new_allowance)


@external
def seed_allocations(_week: uint256, _merkle_root: bytes32, _amount: uint256):
    """
    @notice
        Allocates ldo for merkle reward contract with seed root and week number
        Can only be called by the allocator
    """
    assert msg.sender == self.allocator, "manager: not permitted"
    assert self.is_paused == False, "manager: contract is paused"

    self._update_allowance()

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
    self._update_allowance()
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

    if self.balance != 0:


@external
def pause():
    """
    @notice
        Pause allowance increasing and rejects seedAllocations calling
    """
    assert msg.sender == self.owner, "manager: not permitted"
    self._update_allowance()
    self.is_paused = True

    log Paused(msg.sender)


@external
def unpause():
    """
    @notice
        Unpause allowance increasing and allows seedAllocations calling
    """
    assert msg.sender == self.owner, "manager: not permitted"
    self._update_last_allowance_period_date()
    self.is_paused = False

    log Unpaused(msg.sender)
