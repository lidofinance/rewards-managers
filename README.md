# Balancer rewards manager

This repository contains Lido reward manager contract for [Balancer Merkle Rewards contract](https://github.com/balancer-labs/balancer-v2-monorepo/blob/master/pkg/distributors/contracts/MerkleRedeem.sol).
It periodically approves certain amount of LDO to be spendable by Balancer contract.

# Rewards Manager

The reward manager contract should be set as `owner` of the Balancer Merkle contract.

## Deploying Environment

`DEPLOYER` deployer account

`ALLOCATOR` balancer allocator account

`OWNER` address of manager owner

`START_DATE` timestamp of program start date

## Balancer side

##### `view available_allocations() -> uint256`

Returns current allowance of Reward contract.

##### `seed_allocations(_week: uint256, _merkle_root: bytes32, _amount: uint256):`

Wrapper for `seedAllocations` of Merkle contract. 
Can be called by allocator EOA only.

Reverts if `_amount` is greater than Manager balance or allocations limit.

Events:

```vyper=
event RewardsLimitChanged:
    new_limit: uint256
```

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
Updates current allocations limit and set rewards limit for next periods.

Events:
```vyper=
event RewardsLimitChanged:
    new_limit: uint256
```

##### `change_allocations_limit(_new_allocations_limit: uint256)`

Sets new allocations limit for Reward contract.

Events:
```vyper=
event AllocationsLimitChanged:
    new_limit: uint256
```



##### `pause()`

Stops updating allocations limit and rejects `seed_allocations` calls. Can be called by owner only.

Events:
```vyper=
event Paused:
    actor: address
```

##### `unpause()`

Resumes updating allocations limit and allows `seed_allocations` calls. Can be called by owner only.

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
