# Rewards managers monorepo

------------------------------------

[![Addresses](https://img.shields.io/badge/Addresses-%F0%9F%93%84-blue)](https://docs.lido.fi/deployed-contracts#reward-programs)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

This repository contains manager contracts of the Lido Reward program, along
with their tests, configurations, and deployment information.

### Structure

All rewards managers are stored in `projects` sub-directory.

- [`1inch`](projects/1inch): smart-contracts that implements rewarding management for 1inch liquidity pool (a part of co-incentivization)
- [`ARCx`](projects/arcx): RewardsManager smart contract built for the ARCx's JointCampaign
- [`balancer`](projects/balancer): Lido reward manager contract for [Balancer Merkle Rewards contract](https://github.com/balancer-labs/balancer-v2-monorepo/blob/master/pkg/distributors/contracts/MerkleRedeem.sol)
- [`curve`](projects/curve): Curve reward manager based on a Synthetix `StakingRewards.sol` contract
- [`sushi`](projects/sushi): the implementation of Rewarder for SushiSwap's [MasterChefV2](https://dev.sushi.com/sushiswap/contracts/masterchefv2) contract and helper RewardsManager contract for simplifying managing it via DAO voting
