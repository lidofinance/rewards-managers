# LIDO / 1inch co-incentivization integration

Smart-contracts that implements rewarding management for 1inch liquidity pool (a part of co-incentivization).

## Flow
Deployment, initalization and usage flows are described in separate [FLOW document](./FLOW.md).

## Core contracts

### `RewardsManager.vy`
Contract follows principles from other repositories: [lidofinance/staking-rewards-manager](https://github.com/lidofinance/staking-rewards-manager), [lidofinance/balancer-rewards-manager](https://github.com/lidofinance/balancer-rewards-manager) and [lidofinance/staking-rewards-sushi](https://github.com/lidofinance/staking-rewards-sushi).

Following parts are adapted for compatibility with 1inch [liquidity protocol](https://github.com/1inch/liquidity-protocol) [`FarmingRewards`](https://github.com/1inch/liquidity-protocol/blob/master/contracts/inch/farming/FarmingRewards.sol) contract:
- Added `GIFT_INDEX` constant. This is due to [`FarmingRewards`](https://github.com/1inch/liquidity-protocol/blob/master/contracts/inch/farming/FarmingRewards.sol) contract requires manager contract to be aware of gift index (value dependends on order of [`addGift()`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L144-L161) call).
- Method `_period_finish()` adapted to obtain data from [`FarmingRewards.TokenRewards`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L28) structure, that stores referenced reward data in [`FarmingRewards.tokenRewards`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L36) state variable (of array type).
- Method `start_next_rewards_period()` adapted to transfer reward tokens to `FarmingRewards` instance address and trigger [`FarmingRewards.notifyRewardAmount()`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L96-L120) method. Key points:
  - [`FarmingRewards.notifyRewardAmount()`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L113) requires tokens to be already transfered to `FarmingRewards` instance address.
  - Tokens are [unable to be recovered](https://github.com/1inch/liquidity-protocol/blob/master/contracts/inch/farming/FarmingRewards.sol#L175-L177) after the operation.

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
To test on mainnet fork you neet to set your [Infura](https://infura.io/product/ethereum) project ID first:
```bash
export WEB3_INFURA_PROJECT_ID=YourProjectID
```

Run tests only:
```bash
brownie test
```

Run tests with evaluating coverage and gas usage:
```bash
brownie test --coverage --gas -v
```
