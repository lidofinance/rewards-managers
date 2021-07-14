# Balancer rewards manager

This repository contains Manager contract for Balancer Merkle Rewards contract [...]
It allows to limitate allowance of rewards token for distributing it with Balancer Merkle Rewards contract

# Rewards Manager

This contract should be provided as owner for Balancer Merkle Rewards contract

## Levers

##### `transfer_ownership(_to: address)`

Changes owner. Could be called from owner only

Events:

```vyper=
event OwnerChanged:
    new_owner: address
```

##### `change_allocator(_new_allocator: address)`

Changes allocator. Could be called from owner only

Events:

```vyper=
event AllocatorChanged:
    new_allocator: address
```

##### `change_rewards_limit(_new_limit: uint256)`

Changes reward token limit per period `rewards_period_duration`. Could be called from owner only. 

Events:
```vyper=
event RewardsLimitChanged:
    new_limit: uint256
```

Updates current allowance and set rewards limit for next periods

##### `pause()`

Stops allowance updating and rejects `seedAllowance` calling. Could be called from owner only.

Events:
```vyper=
event Paused:
    actor: address
```

##### `unpause()`

Resume allowance updating and allows `seedAllowance` calling. Could be called from owner only.

Events:
```vyper=
event Unpaused:
    actor: address
```

##### `recover_erc20(_token: address, _recipient: address = msg.sender)`

Transfers the whole balance of the given ERC20 token from self to the recipient. Could be called from owner only.


Events:
```vyper=
event ERC20TokenRecovered:
    token: address
    amount: uint256
    recipient: address
```


# Balancer side

##### `view allowance() -> uint256`

Returns current allowance of Reward contract

##### `seedAllocations(_week: uint256, _merkle_root: bytes32, _amount: uint256):`

Wrapper for `seedAllocations` of Merkle contract. 
Could be called from allocator EOA only

Reverts if `_amount` is bigger then Manager balance or allowance

Events:

```vyper=
event RewardsLimitChanged:
    new_limit: uint256
```