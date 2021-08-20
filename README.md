# LIDO / 1inch co-incentivization integration

Smart-contracts that implements rewarding management for 1inch liquidity pool (a part of co-incentivization).

## Flow
Deployment, initalization and usage flows are described in separate [FLOW document](./FLOW.md).

## Core contracts

### `RewardsManager.vy`
Contract follows principles from other repositories: [lidofinance/staking-rewards-manager](https://github.com/lidofinance/staking-rewards-manager), [lidofinance/balancer-rewards-manager](https://github.com/lidofinance/balancer-rewards-manager) and [lidofinance/staking-rewards-sushi](https://github.com/lidofinance/staking-rewards-sushi).

Following parts are adapted for compatibility with 1inch [liquidity protocol](https://github.com/1inch/liquidity-protocol) `FarmingRewards`(https://github.com/1inch/liquidity-protocol/blob/master/contracts/inch/farming/FarmingRewards.sol) contract:
- Added `gift_index` state variable and corresponding setter `set_gift_index()`. This is due to `FarmingRewards` contract requires manager contract to be aware of gift index (value dependends on order of [`addGift()`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L144-L161) call).
- Method `_period_finish()` adapted to obtain data from [`FarmingRewards.TokenRewards`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L28) strcutre, that stores referenced reward data in [`FarmingRewards.tokenRewards`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L36) array.
- Method `start_next_rewards_period()` adapted to transfer reward tokens to `FarmingRewards` instance address and trigger [`FarmingRewards.notifyRewardAmount()`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L96-L120) method. Key notes:
  - [`FarmingRewards.notifyRewardAmount()`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L113) requires tokens to be already transfered to `FarmingRewards` instance address.
  - Tokens are [unable to be recovered](https://github.com/1inch/liquidity-protocol/blob/master/contracts/inch/farming/FarmingRewards.sol#L175-L177) after this operation.

### `Vendor.sol`
Flattened version of 1inch [FarmingRewards](https://github.com/1inch/liquidity-protocol/blob/master/contracts/inch/farming/FarmingRewards.sol) and [MooniswapFactoryGovernance](https://github.com/1inch/liquidity-protocol/blob/master/contracts/governance/MooniswapFactoryGovernance.sol). This is considered as a vendor code:
- Not supposed to have any local changes.
- Used only for the tests.
- Entities expected to be deployed prior to `RewardsManager.vy`.

### `Mocks.sol`
Custom contracts, stubs, mocks and whatever else, that is needed to support simulation and tests. Not intended to be used in production.

## Installation
To use the tools provided by this project, please pull the repository from GitHub and install its dependencies as follows. It is recommended to use a Python virtual environment.
```bash
npm install
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements-dev.txt
```
Compile the smart contracts:
```bash
brownie compile # add `--size` to see contract compiled sizes
```

## Test
To test on a local development network run:
```bash
brownie test
```
To test on mainnet fork you neet to set your [Infura](https://infura.io/product/ethereum) project ID first:
```bash
export WEB3_INFURA_PROJECT_ID=YourProjectID
brownie test --network mainnet-fork
```
