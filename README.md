# SushiSwap Staking Rewards

Fork of [lidofinance/staking-rewards-manager](https://github.com/lidofinance/staking-rewards-manager) repository.

Contains the implementation of Rewarder for SushiSwap's MasterChefV2 contract and helper RewardsManager contract for simplifying its management using DAO voting. Rewarder based on Synthetix's [StakingRewards.sol](https://github.com/lidofinance/staking-rewards-manager/blob/main/contracts/StakingRewards.sol) contract which Lido has already used in Curve's liquidity pool.

## Core Contracts

### StakingRewards.sol

To use StakingRewards contract as a base contract for SushiRewarder next changes were applied to StakingRewards.sol contract:

- Methods `stake(uint256 amount)`, `withdraw(uint256 amount)`, and `exit()` were removed. MasterChefV2 will take control over this operations.
- External method `getReward()` was replaced with the internal method `_payReward(address user, address recipient)` which allows paying rewards of the user to another `recipient`'s address.
- Since reward might be paid to address different from user's address event `RewardPaid(address indexed user, uint256 reward)` was changed in a next manner `RewardPaid(address indexed user, address indexed recipient, uint256 reward)`.
- Events `Staked` and `Withdrawn` were removed as not used anymore.
- Method `totalSupply()` was marked as abstract and its visibility was changed to public.
- Variable `_totalSupply` was removed and all its usages were replaced with `totalSupply()` view.
- Constructor of the contract became internal cause the contract is abstract now and can't be deployed.
- Visibility of `_balances` variable was changed from `private` to `internal`. This is necessary to make it accessible in the child contracts.

The above changes don't touch rewards calculation logic and only modifies the interface of a contract to make it possible to use it as a base contract for different rewarder contracts. For example, we can implement the current Lido's Curve contract using the modified StakingRewards contract as a base contract, or implement a rewarder for SushiSwap's liquidity pool.

### StakingRewardsSushi.sol

Inherits logic of StakingRewards contract and implements Sushi's `IRewarder` interface to make it possible to use as a rewarder in MasterChefV2 contract.

To be used in MasterChefV2 contract it has to implement next interface:

```solidity=
interface IRewarder {
    function onSushiReward(
        uint256 pid,
        address user,
        address recipient,
        uint256 sushiAmount,
        uint256 newLpAmount
    ) external;

    function pendingTokens(
        uint256 pid,
        address user,
        uint256 sushiAmount
    ) external view returns (IERC20[] memory, uint256[] memory);
}
```

Method `pendingTokens` is used by SushiSwaps's UI and must return a tuple with a list of rewardTokens distributes by the rewarder and a list of amounts of tokens gained by the user.
In current implementation `SushiStakingRewards` distributes only one `rewardsToken`, and returns next value from `pendingTokens` method: `([rewardsToken], [earned(msg.sender)])`

Method `onSushiReward` is executed on the distribution of rewards with the user and the amount of Sushi given out being specified or on any change of balance of user's lpTokens. In the current implementation, this method validates that method was called by MasterChefV2 contract with correct pid value, calls method `_payReward(user, recipient)` and updates user balance.

To be deployable `SushiStakingRewards` implements abstract method `totalSupply()` from `StakingRewards.sol` contract in next way:

```solidity=
function totalSupply() public view returns (uint256) {
    return stakingToken.balanceOf(MASTERCHEF_V2);
}
```

where `MASTERCHEF_V2` is an address of MasterChefV2 contract.

### RewardsManager.vy

This contract simplifies operations with reward periods of StakingRewards contracts for DAO. Was used without any changes from the original repository.

## Project Setup

To use the tools that this project provides, please pull the repository from GitHub and install its dependencies as follows. It is recommended to use a Python virtual environment.

```bash
git clone https://github.com/lidofinance/staking-rewards-sushi
cd staking-rewards-sushi
npm install
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements-dev.txt
```

Compile the Smart Contracts:

```bash
brownie compile # add `--size` to see contract compiled sizes
```

## Scripts

### `deploy.py`

Contains script to deploy `StakingRewardsSushi` and `RewardsManager` contracts. The script requires `DEPLOYER` ENV variable be set.
