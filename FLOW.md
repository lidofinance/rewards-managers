# Flow

## Involved entities

- LDO token - [`0x5a98fcbea516cf06857215779fd812ca3bef1b32`](https://etherscan.io/token/0x5a98fcbea516cf06857215779fd812ca3bef1b32)
- stETH token - [`0xae7ab96520de3a18e5e111b5eaab095312d7fe84`](https://etherscan.io/token/0xae7ab96520de3a18e5e111b5eaab095312d7fe84)
- DAI token - [`0x6b175474e89094c44da98b954eedeac495271d0f`](https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f)
- 1INCH token - [`0x111111111117dc0aa78b770fa6a738034120c302`](https://etherscan.io/token/0x111111111117dc0aa78b770fa6a738034120c302)
- 1INCH liquidity pool - [`Mooniswap`](https://github.com/1inch/liquidity-protocol/blob/master/contracts/Mooniswap.sol)
- 1INCH rewards contract - [`FarmingRewards`](https://github.com/1inch/liquidity-protocol/blob/master/contracts/inch/farming/FarmingRewards.sol)
- LIDO rewards manager - [`RewardsManager`](https://github.com/maddevsio/lido/blob/main/contracts/RewardsManager.sol)

## Deployment and initialization flow

1. **LDO** token is deployed.
2. **1INCH** token is deployed.
3. **DAI** token is deployed.
4. **stETH** token is deployed.
5. `Mooniswap` is deployed:
    - Pair of tokens is **stETH** and **DAI**.
    - `Mooniswap` provides **LP** tokens as result of depositing.
6. `FarmingRewards` is deployed:
    - Target pool is previously deployed `Mooniswap`.
    - Initial gift is **1INCH** token (**scale** and **duration** are TBD).
    - Initial gift distribution is TBD, but expected to be related to 1INCH.
    - Initial gift reserves index `0` in `tokenRewards` array.
7. `RewardsManager` is deployed:
    - Expected gift index is set to `1`.
    - Target rewards contract is previously deployed `FarmingRewards`.
    - Target rewards token is **LDO token**.
8. `FarmingRewards` owner adds new gift (calls `addGift()`):
    - Gift token is **LDO**.
    - Gift distribution is `RewardsManager`.
    - Gift is REQUIRED to be at index `1` in `tokenRewards` array (this MUST match with `giftIndex`).
9. LIDO triggers new reward period (via Aragon Voting):
    - **LDO** tokens is transferred to an address of `RewardsManager`.
    - Method `start_next_rewards_period()` is called on `RewardsManager`.
        - `RewardsManager` transfers all **LDO** tokens to an address of `FarmingRewards`.
        - `RewardsManager` calls method `notifyRewardAmount()` method on `FarmingRewards`.
        - **LDO** tokens CAN NOT be recovered (via `recover_erc20()` method call) after this action.

## Usage flow

1. There is a **User**, that has **stETH** and **DAI** tokens.
2. **User** calls method `deposit()` on `Mooniswap` and provides **stETH** and **DAI** tokens.
    - **User** receives **LP** tokens as the result.
3. **User** calls method `approve()` on `Mooniswap`.
    - Recipient is `FarmingRewards`.
    - Amount is TBD.
4. **User** calls method `stake()` on `FarmingRewards`.
    - **User** receives staking tokens as the result.
5. After some time **User** calls method `exit()` on `FarmingRewards`.
    - **User** looses all staking tokens.
    - **User** receives **LP**, **1INCH** and **LDO** tokens as the result.
6. **User** calls method `withdraw()` on `Mooniswap`.
    - **User** looses **LP** tokens.
    - **User** receives **stETH** and **DAI** tokens (including rewards).
    - **User** still has **1INCH** and **LDO** tokens.

## Visual diagram of the flow
![Visual diagram](/FLOW.png)