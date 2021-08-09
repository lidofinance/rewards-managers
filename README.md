# LIDO / 1inch co-incentivization flow

## Prerequisites
```bash
npm install -g ganache-cli
```

## Installation
```bash
npm install
```

## Structure
```text
├── contracts                     # Solidity sources
│   ├── Custom.sol                # Custom contracts that are mocks or helpers to support flow simulation
│   ├── FarmingRewards.sol        # Fattened source of 1INCH rewards farming contract and it's dependencies
│   ├── Migrations.sol            # Common truffle migrations source
│   └── RewardsManager.sol        # Reward manager implementation
├── migrations
│   └── 1_initial_migration.js    # Migrations deployment script
├── package.json                  # NPM dependencies and project configuration file
├── README.md                     # Project README file
├── test                          # Acceptance tests
│   └── flow.spec.js              # Full flow simulation
└── truffle-config.js             # Truffle project configuration file
```
Key points:
- Flow simulation is in [`test/flow.spec.js`](https://github.com/maddevsio/lido/blob/main/test/flow.spec.js) file.
- Contract sources are in [`contracts`](https://github.com/maddevsio/lido/tree/main/contracts) directory:
  - [`FarmingRewards.sol`](https://github.com/maddevsio/lido/blob/main/contracts/FarmingRewards.sol) - flattened version of 1inch [FarmingRewards](https://github.com/1inch/liquidity-protocol/blob/master/contracts/inch/farming/FarmingRewards.sol) and [MooniswapFactoryGovernance](https://github.com/1inch/liquidity-protocol/blob/master/contracts/governance/MooniswapFactoryGovernance.sol).
  - [`Custom.sol`](https://github.com/maddevsio/lido/blob/main/contracts/Custom.sol) - custom contracts, stubs and whatever else, that is created by us.
  - [`RewardsManager.sol`](https://github.com/maddevsio/lido/blob/main/contracts/RewardsManager.sol) - reward manager implementation that is intended to deploy and use for the integration.

## Performing simulation
- In terminal 1:
  ```bash
  npm run ganache
  ```
- In terminal 2:
  ```bash
  npm run compile # if any Solidity sources were changed
  npm test
  ```

It is better to restart Ganache CLI after test runs to have clean environment.

## Tools
To flatten Solidity sources [solc-typed-ast](https://github.com/ConsenSys/solc-typed-ast/) may be used in following way:
```bash
sol-ast-compile path/to/file.sol --source
```
