# LIDO / 1inch co-incentivization flow

## Flow
Deployment, initalization and usage flows are described in separate [FLOW document](./FLOW.md).

## Components versions
- solc: 0.6.12
- truffle: 5.4.3
- ganache-core: 2.13.0
- solidity-coverage: 0.7.16

## Prerequisites
- Install [NodeJS 12](https://nodejs.org/en/) or higher with NPM (or use [NVM](https://github.com/nvm-sh/nvm)).
- Install [Ganache CLI](https://www.npmjs.com/package/ganache-cli):
  ```bash
  npm install -g ganache-cli
  ```

## Installation
```bash
npm install
```

## Structure
```text
├── build                         # Truffle artifacts
├── coverage                      # Coverage reports
├── contracts                     # Smart-contract implementations (solidity sources)
│     ├── Migrations.sol          # Common truffle migrations source
│     ├── Mocks.sol               # Custom contracts that are mocks or helpers to support flow simulation
│     ├── RewardsManager.sol      # Reward manager implementation
│     └── Vendor.sol              # Fattened source of 1INCH rewards farming contract and it's dependencies
├── migrations                    # Deployment script
│     └── 1_initial_migration.js  # Migrations contract deployment script
├── package.json                  # NPM dependencies and project configuration file
├── README.md                     # Project README file
├── test                          # Acceptance tests
│     └── flow.spec.js            # Full flow simulation
└── truffle-config.js             # Truffle project configuration file
```
Key points:
- Flow simulation is in [`test/flow.spec.js`](https://github.com/maddevsio/lido/blob/main/test/flow.spec.js) file.
- Contract sources are in [`contracts`](https://github.com/maddevsio/lido/tree/main/contracts) directory:
  - [`Vendor.sol`](https://github.com/maddevsio/lido/blob/main/contracts/Vendor.sol) - flattened version of 1inch [FarmingRewards](https://github.com/1inch/liquidity-protocol/blob/master/contracts/inch/farming/FarmingRewards.sol) and [MooniswapFactoryGovernance](https://github.com/1inch/liquidity-protocol/blob/master/contracts/governance/MooniswapFactoryGovernance.sol).
  - [`Mocks.sol`](https://github.com/maddevsio/lido/blob/main/contracts/Mocks.sol) - custom contracts, stubs, mocks and whatever else, that is created by us to support simulation. Not intended to be used in production.
  - [`RewardsManager.sol`](https://github.com/maddevsio/lido/blob/main/contracts/RewardsManager.sol) - reward manager implementation that is intended to deploy and be used for the integration.

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

## Test coverage
Use following command to generate tests coverage reports:
```bash
npm run coverage
```

## Tools
To flatten Solidity sources [solc-typed-ast](https://github.com/ConsenSys/solc-typed-ast/) may be used in following way:
```bash
sol-ast-compile path/to/file.sol --source
```
