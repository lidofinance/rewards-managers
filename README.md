# Flow simulation setup

## Prerequisites
```bash
npm install -g ganache-cli
```

## Installation
```bash
npm install
```

## Structure
- Flow simulation is in `test/flow.spec.js` file.
- Contract sources are in `contracts` directory:
  - `FarmingRewards.sol` - flattened version of 1inch [FarmingRewards](https://github.com/1inch/liquidity-protocol/blob/master/contracts/inch/farming/FarmingRewards.sol) and [MooniswapFactoryGovernance](https://github.com/1inch/liquidity-protocol/blob/master/contracts/governance/MooniswapFactoryGovernance.sol).
  - `Custom.sol` - custom contracts, stubs and whatever else, that is created by us.

## Performing simulation
- In terminal 1:
  ```bash
  ganache-cli -l 9000000000000000 -g 0 --allowUnlimitedContractSize
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
