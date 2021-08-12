### Terms

**LP** - liquidity provider, the user who deposits the liquidity to the pool and gets rewarded for that.

**Incentivization** - additional rewarding of LP for some particular pool in some specific tokens. In our case, we want to reward LP of stETH - DAI pool with LDO and INCH.

**Co-incentivization** - incentivization from two sides with two tokens. In our case, Lido and 1inch co-incentivize LP of stETH - DAI pool with LDO and INCH.

### Background

Initially (and currently), almost all the stETH liquidity was allocated to Curve. Having all the liquidity in one pool is a problem for integrations because of related risks.

Lido decided to diversify liquidity to multiple pools ([governance proposal](https://research.lido.fi/t/diversify-liquidity-pools-to-boost-steth-integrations/729)).

One of the pools to launch is 1inch. We agreed on co-incentivization with 1inch (rewarding liquidity providers by rewards in LDO and INCH tokens additional to standard LP rewards)

### About 1inch farming

1. A user provides the target token(s) into a liquidity pool, getting the LP (liquidity provider) tokens in return.
2. If there is FarmingRewards is deployed for that pool, the user can deposit the LP tokens into it. And as an exchange, he provided with staking tokens.
3. TODO: write down how INCH tokens are deposited into FarmingRewards contract

#### How farming works on 1inch
TODO: write down about how farming works (no docs have been found)

### Adding LDO rewards
The proposal is to develop and deploy RewardsManager contract which will be funded with LDO tokens by Lido DAO voting.

RewardsManager contract expects to be triggered by DAO voting and LDO tokens to be transferred to it. The contract is triggered by a call on start_next_rewards_period function which calls notifyRewardAmount on 1inch’s FarmingRewards contract and LDO tokens transferred to it. 1inch’s FarmingRewards then handles any interactions from the user who deposited his LP tokens to participate in yield farming program.

###  DAO routine operations
Initially, the DAO votes to approve the deployed RewardsManager contract to spend the amount of unassigned LDO tokens that’s enough for, say, several months of rewards.

Each week (or any other period agreed upon) the DAO initiates a vote to start a new reward period and distribute some amount of LDO tokens as LP reward (e.g. to call start_next_rewards_period on RewardsManager which calls notifyRewardAmount on 1inch’s FarmingRewards contract).


When the allowance for the rewards contract to spend LDO becomes insufficient to start a new rewards period, the DAO initiates a vote to increase the allowance.

