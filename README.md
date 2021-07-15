# Balancer rewards manager

This repository contains Lido reward manager contract for Balancer Merkle Rewards contract.
It periodically approves certain amount of LDO to be spendable by Balancer contract.

# Rewards Manager

The reward manager contract should be set as `owner` of the Balancer Merkle contract.

## Deploying Environment

`DEPLOYER` deployer account

`ALLOCATOR` balancer allocator account

`MERKLE_CONTRACT` address of Merkle contract

`OWNER` address of manager owner


## Levers

##### `transfer_ownership(_to: address)`

Changes `OWNER`. Can be called by owner only.

Events:

```vyper=
event OwnerChanged:
    new_owner: address
```

##### `change_allocator(_new_allocator: address)`

Changes `ALLOCATOR`. Can be called by owner only.

Events:

```vyper=
event AllocatorChanged:
    new_allocator: address
```

##### `change_rewards_limit(_new_limit: uint256)`

Changes reward token limit per period `rewards_period_duration`. Can be called by owner only. 

Events:
```vyper=
event RewardsLimitChanged:
    new_limit: uint256
```

Updates current allowance and set rewards limit for next periods.

##### `pause()`

Stops updating allowance and rejects `seedAllowance` calls. Can be called by owner only.

Events:
```vyper=
event Paused:
    actor: address
```

##### `unpause()`

Resumes updating allowance and allows `seedAllowance` calls. Can be called by owner only.

Events:
```vyper=
event Unpaused:
    actor: address
```

##### `recover_erc20(_token: address, _recipient: address = msg.sender)`

Transfers the whole balance of the given ERC20 token to the recipient. Can be called by owner only.


Events:
```vyper=
event ERC20TokenRecovered:
    token: address
    amount: uint256
    recipient: address
```


# Balancer side

##### `view allowance() -> uint256`

Returns current allowance of Reward contract.

##### `seed_allocations(_week: uint256, _merkle_root: bytes32, _amount: uint256):`

Wrapper for `seedAllocations` of Merkle contract. 
Can be called by allocator EOA only.

Reverts if `_amount` is greater than Manager balance or allowance.

Events:

```vyper=
event RewardsLimitChanged:
    new_limit: uint256
```
