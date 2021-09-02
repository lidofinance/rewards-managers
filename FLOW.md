# Flow

## Involved entities

- LDO token - [`0x5a98fcbea516cf06857215779fd812ca3bef1b32`](https://etherscan.io/token/0x5a98fcbea516cf06857215779fd812ca3bef1b32)
- stETH token - [`0xae7ab96520de3a18e5e111b5eaab095312d7fe84`](https://etherscan.io/token/0xae7ab96520de3a18e5e111b5eaab095312d7fe84)
- DAI token - [`0x6b175474e89094c44da98b954eedeac495271d0f`](https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f)
- 1INCH token - [`0x111111111117dc0aa78b770fa6a738034120c302`](https://etherscan.io/token/0x111111111117dc0aa78b770fa6a738034120c302)
- 1INCH liquidity pool - [`Mooniswap`](https://etherscan.io/address/0xC1A900Ae76dB21dC5aa8E418Ac0F4E888A4C7431) ([source](https://github.com/1inch/liquidity-protocol/blob/master/contracts/Mooniswap.sol))
- 1INCH rewards contract - [`FarmingRewards`](https://etherscan.io/address/0xd7012cdebf10d5b352c601563aa3a8d1795a3f52) ([source](https://github.com/1inch/liquidity-protocol/blob/master/contracts/inch/farming/FarmingRewards.sol))
- LIDO rewards manager - [`RewardsManager`](https://github.com/maddevsio/lido/blob/main/contracts/RewardsManager.vy)

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
    - Initial gift reserves index `0` in [`tokenRewards`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L36) array.
7. `RewardsManager` is deployed:
    - `GIFT_INDEX` constant value is set to `1`.
    - Target rewards contract is previously deployed `FarmingRewards`.
    - Target rewards token is **LDO token**.
8. `FarmingRewards` owner adds new gift (calls [`addGift()`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L144-L161)):
    - Gift token is **LDO**.
    - Gift distribution is `RewardsManager`.
    - Gift is REQUIRED to be at index `1` in [`tokenRewards`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L36) array (this MUST match with `GIFT_INDEX` constant value in `RewardsManager`).
    - Gift `scale` and `duration` have to be determined **carefully**:
        - Method [`addGift()`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L144-L161) has a very basic check for `scale` and no check for duration.
        - Method [`notifyRewardAmount()`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L96-L120) has more strong math-based checks. This means that if gift added with improper `scale` and `duration`, then [`notifyRewardAmount()`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L96-L120) will not allow to start rewarding period until these parameters are properly adjusted via [`setDuration()`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L128-L133) and/or [`setScale()`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L135-L142).
9. LIDO triggers new reward period (via Aragon Voting):
    - **LDO** tokens is transferred to an address of `RewardsManager`.
    - Method `start_next_rewards_period()` is called on `RewardsManager`.
        - `RewardsManager` transfers all **LDO** tokens to an address of `FarmingRewards`.
        - `RewardsManager` calls method [`notifyRewardAmount()`](https://github.com/1inch/liquidity-protocol/blob/d0c38df6703ac965dacbe09a9c61a5f8366152f1/contracts/utils/BaseRewards.sol#L96-L120) method on `FarmingRewards`.
        - **LDO** tokens CAN NOT be recovered (via `recover_erc20()` method call or [`rescueFunds()`](https://github.com/1inch/liquidity-protocol/blob/master/contracts/inch/farming/FarmingRewards.sol#L174-L183)) after this action.

## Usage flow

1. There is a **User**, that has **stETH** and **DAI** tokens.
2. **User** calls method `deposit()` on `Mooniswap` and provides **stETH** and **DAI** tokens.
    - **User** receives **LP** tokens as the result.
3. **User** calls method `approve()` on `Mooniswap`.
    - Recipient is `FarmingRewards`.
    - Amount is TBD.
4. **User** calls method `stake()` on `FarmingRewards`.
    - **User** receives staking tokens as the result.
5. After some time **User** calls method `claim()` on `FarmingRewards`.
    - **User** receives **1INCH** and **LDO** tokens as the result.
    - **LP tokens** are left in `FarmingRewards`.
6. **User** calls method `withdraw()` on `FarmingRewards`.
    - **User** receives his **LP tokens**.
    - **1INCH** and **LDO** are left in `FarmingRewards`.
7. **User** calls method `exit()` on `FarmingRewards`.
    - **User** receives **1INCH** and **LDO** tokens as the result.
    - **User** receives his **LP tokens**.

## Visual diagram of the flow
![Visual diagram](/FLOW.png)
