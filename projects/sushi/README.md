# SushiSwap Staking Rewards

Fork of [lidofinance/staking-rewards-manager](https://github.com/lidofinance/staking-rewards-manager) repository.

Contains the implementation of Rewarder for SushiSwap's [MasterChefV2](https://dev.sushi.com/sushiswap/contracts/masterchefv2) contract and helper RewardsManager contract for simplifying managing it via DAO voting. Rewarder is based on Synthetix's [StakingRewards.sol](https://github.com/lidofinance/staking-rewards-manager/blob/main/contracts/StakingRewards.sol) contract which Lido has previously used in Curve's liquidity pool.

## Core Contracts

### StakingRewards.sol

To use StakingRewards contract as a base contract for SushiRewarder, the following changes have been applied to [StakingRewards.sol](https://github.com/lidofinance/staking-rewards-manager/blob/main/contracts/StakingRewards.sol) contract:

- Methods `stake(uint256 amount)`, `withdraw(uint256 amount)`, and `exit()` have been removed. MasterChefV2 will take control over these operations.
- External method `getReward()` has been replaced by the internal method `_payReward(address user, address recipient)` which allows paying user's rewards to another `recipient`'s address.
- Since reward might be paid to address different from user's address, event `RewardPaid(address indexed user, uint256 reward)` has been changed as follows: `RewardPaid(address indexed user, address indexed recipient, uint256 reward)`.
- Events `Staked` and `Withdrawn` have been removed as unnecessary.
- Method `totalSupply()` has been marked as abstract and it's visibility changed to public.
- Variable `_totalSupply` has been removed and replaced by `totalSupply()` view everywhere.
- Constructor of the contract have become internal because the contract is abstract now and can't be deployed.
- Visibility of `_balances` variable has been changed from `private` to `internal`. This is necessary to make it accessible in the child contracts.
- Method `updatePeriodFinish(uint timestamp)` has been added (method has been also added into original Synthetix's StakingRewards contract after creation of repo [lidofinance/staking-rewards-manager](https://github.com/lidofinance/staking-rewards-manager)). This method might be helpful for emergency stop of reward distribution (`periodFinish` value might be set to past block, and new rewards will not be distributed.)

The above changes don't involve rewards calculation logic and only modify the interface of the contract to make it possible to use it as a base contract for different rewarder contracts. For example, we can implement the current Lido's Curve contract using the modified StakingRewards contract as a base contract, or implement a rewarder for SushiSwap's liquidity pool.

### StakingRewardsSushi.sol

Inherits logic from StakingRewards contract and implements Sushi's `IRewarder` interface to make it possible to use as a rewarder in [MasterChefV2](https://dev.sushi.com/sushiswap/contracts/masterchefv2) contract.

To be used in MasterChefV2 contract, it has to implement the following interface:

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

Method `pendingTokens` is used by SushiSwap's UI and must return a tuple with a list of rewardTokens distributed by the rewarder and a list of amounts of tokens gained by the user.
In current implementation `SushiStakingRewards` distributes only one `rewardsToken`, and returns next value from `pendingTokens` method: `([rewardsToken], [earned(msg.sender)])` if was passed correct `pid` value. Returns tuple with empty arrays in other cases.

Method `onSushiReward` is executed on the distribution of rewards with the user and the amount of Sushi given out being specified, or on any change of user's balance of `stakingToken`. In the current implementation, this method validates that method has been called by MasterChefV2 contract with correct pid value, calls method `_payReward(user, recipient)` and updates user balance in `_balances` mapping.

To be deployable, `SushiStakingRewards` implements abstract method `totalSupply()` from `StakingRewards.sol` contract as follows:

```solidity=
function totalSupply() public view returns (uint256) {
    return stakingToken.balanceOf(MASTERCHEF_V2);
}
```

where `MASTERCHEF_V2` is the address of MasterChefV2 contract.

To make `StakingRewardsSushi` rewarder compatible with SushiSwap's default UI, the next view methods were added:

- `rewardPerSecond()` - returns `rewardRate` value from base `StakingRewards` contract if current reward period hasn't finished yet (current block timestamp is less than `periodFinish` value) and 0 in other cases.
- `rewardToken()` - returns value of `rewardsToken` variable from base `StringRewards` contract

### RewardsManager.vy

This contract simplifies operations with reward periods of StakingRewards contracts for the DAO.
Compared to the original repository next changes were applied:

- Was added method `period_finish()` which returns end of the rewards period of `StakingRewards` contract. This method will help retrieve all info required to start a new reward period directly from the manager contract.
- Method `recover_erc20()` now accepts `_amount` as the second argument to allow recovery of the exact amount of tokens instead of the whole balance.

## Project Setup

To use the tools provided by this project, please pull the repository from GitHub and install its dependencies as follows. It is recommended to use a Python virtual environment.

```bash
git clone https://github.com/lidofinance/staking-rewards-sushi
cd staking-rewards-sushi
npm install
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements-dev.txt
```

Compile the smart contracts:

```bash
brownie compile # add `--size` to see contract compiled sizes
```

## Scripts

### `deploy.py`

Contains script to deploy `StakingRewardsSushi` and `RewardsManager` contracts. The script requires `DEPLOYER` ENV variable be set.
