const StubERC20 = artifacts.require("StubERC20");
const Mooniswap = artifacts.require("Mooniswap");
const MooniswapFactoryGovernance = artifacts.require("MooniswapFactoryGovernance");
const FarmingRewards = artifacts.require("FarmingRewards");
const RewardsManager = artifacts.require("RewardsManager");

async function deployToken(name, sym, supply, owner) {
    const token = await StubERC20.new(name, sym, supply, { from: owner });

    assert.equal((await token.balanceOf(owner)).toNumber(), supply);

    return token;
}

async function deployRewardsManager(owner, giftIndex, rewards, token) {
    const rewardsManager = await RewardsManager.new(giftIndex, rewards.address, token.address, { from: owner });

    return rewardsManager;
}

async function startNextRewardPeriod(rewardsManager, token, tokenOwner, tokenAmount, rewards) {
    const rmBalanceBefore = (await token.balanceOf(rewardsManager.address)).toNumber();

    assert.equal(rmBalanceBefore, 0);

    /**
     * Tokens are transferred to RewardManager first.
     * For simplicity, just send LDO tokens instead of using full Aragon Voting flow
     * (that is considered "just working").
     */
    await token.transfer(rewardsManager.address, tokenAmount, { from: tokenOwner });

    const rmBalanceAfterTransfer = (await token.balanceOf(rewardsManager.address)).toNumber();

    assert.equal(rmBalanceAfterTransfer, tokenAmount);

    /**
     * Transfers tokens to FarmingRewards and triggering new reward period.
     */
    await rewardsManager.start_next_rewards_period();

    const rmBalanceAfterPeriodStart = (await token.balanceOf(rewardsManager.address)).toNumber();
    const rBalanceAfterPeriodStart = (await token.balanceOf(rewards.address)).toNumber();

    /**
     * RewardManager transfered all of the tokens to FarmingRewards, so:
     * - balance decreased for RewardManager.
     * - balance increased for FarmingRewards.
     * - balance of FarmingRewards is amount of tokens.
     */
    assert.equal(rmBalanceAfterPeriodStart, 0);
    assert.equal(rBalanceAfterPeriodStart, tokenAmount);
}

async function deployPoolAndRewards(owner, token0, token1, giftToken, distribution, duration, scale) {
    const factory = await MooniswapFactoryGovernance.new(
        '0x0000000000000000000000000000000000000000',   // Do not care just yet
        { from: owner }
    );

    const pool = await Mooniswap.new(
        token0.address,
        token1.address,
        "stETH-DAI Liquidity Pool Token",
        "LP",
        factory.address,
        { from: owner }
    );

    assert.equal((await pool.token0()).valueOf(), token0.address);
    assert.equal((await pool.token1()).valueOf(), token1.address);

    const rewards = await FarmingRewards.new(
        pool.address,
        giftToken.address,
        duration,
        distribution,
        scale,
        { from: owner }
    );

    return [pool, rewards];
}

async function giveTokens(token, owner, user, amount) {
    const ownerBalanceBefore = (await token.balanceOf(owner)).toNumber();

    await token.transfer(user, amount, { from: owner });

    const ownerBalanceAfter = (await token.balanceOf(owner)).toNumber();

    assert.equal((await token.balanceOf(user)).toNumber(), amount);
    assert.equal(ownerBalanceAfter, ownerBalanceBefore - amount);
}

async function provideLiquidityToPool(user, pool, t0, t1, maxAmounts, minAmounts) {
    const t0BalanceBefore = (await t0.balanceOf(user)).toNumber();
    const t1BalanceBefore = (await t1.balanceOf(user)).toNumber();

    await t0.approve(pool.address, maxAmounts[0], { from: user });
    await t1.approve(pool.address, maxAmounts[1], { from: user });

    await pool.deposit(maxAmounts, minAmounts, { from: user });

    const t0BalanceAfter = (await t0.balanceOf(user)).toNumber();
    const t1BalanceAfter = (await t1.balanceOf(user)).toNumber();

    /**
     * User token balance decreased. Pool token balance increased.
     * For both tokens that user deposited.
     */
    assert.isBelow(t0BalanceAfter, t0BalanceBefore);
    assert.equal((await t0.balanceOf(pool.address)).toNumber(), t0BalanceBefore - t0BalanceAfter);

    assert.isBelow(t1BalanceAfter, t1BalanceBefore);
    assert.equal((await t1.balanceOf(pool.address)).toNumber(), t1BalanceBefore - t1BalanceAfter);

    /**
     * User should receive LP tokens from pool
     */
    assert.isAbove((await pool.balanceOf(user)).toNumber(), 0);
}

async function stakeToRewards(user, pool, rewards) {
    const lpUserBalanceBefore = (await pool.balanceOf(user)).toNumber();
    const lpRewardsBalanceBefore = (await pool.balanceOf(rewards.address)).toNumber();
    const stUserBalanceBefore = (await rewards.balanceOf(user)).toNumber();

    assert.isAbove(lpUserBalanceBefore, 0);
    assert.equal(lpRewardsBalanceBefore, 0);
    assert.equal(stUserBalanceBefore, 0);

    await pool.approve(rewards.address, lpUserBalanceBefore, { from: user });
    await rewards.stake(lpUserBalanceBefore, { from: user });

    const lpUserBalanceAfter = (await pool.balanceOf(user)).toNumber();
    const lpRewardsBalanceAfter = (await pool.balanceOf(rewards.address)).toNumber();
    const stUserBalanceAfter = (await rewards.balanceOf(user)).toNumber();

    assert.equal(lpRewardsBalanceAfter, lpUserBalanceBefore);
    assert.equal(lpUserBalanceAfter, 0);
    assert.isAbove(stUserBalanceAfter, 0);
}

async function exitFromRewards(user, pool, rewards) {
    const lpUserBalanceBefore = (await pool.balanceOf(user)).toNumber();
    const lpRewardsBalanceBefore = (await pool.balanceOf(rewards.address)).toNumber();

    assert.equal(lpUserBalanceBefore, 0);
    assert.isAbove(lpRewardsBalanceBefore, 0);

    await rewards.exit({ from: user });

    const lpUserBalanceAfter = (await pool.balanceOf(user)).toNumber();
    const lpRewardsBalanceAfter = (await pool.balanceOf(rewards.address)).toNumber();

    assert.equal(lpUserBalanceAfter, lpRewardsBalanceBefore);
    assert.equal(lpRewardsBalanceAfter, 0);
}

async function withdrawLiquidityFromPool(user, pool, t0, t1) {
    const lpUserBalanceBefore = (await pool.balanceOf(user)).toNumber();
    const t0UserBalanceBefore = (await t0.balanceOf(user)).toNumber();
    const t1UserBalanceBefore = (await t1.balanceOf(user)).toNumber();
    const t0PoolBalanceBefore = (await t0.balanceOf(pool.address)).toNumber();
    const t1PoolBalanceBefore = (await t1.balanceOf(pool.address)).toNumber();

    const minAmounts = [1000, 1000];

    await pool.withdraw(lpUserBalanceBefore, minAmounts, { from: user });

    const lpUserBalanceAfter = (await pool.balanceOf(user)).toNumber();
    const t0UserBalanceAfter = (await t0.balanceOf(user)).toNumber();
    const t1UserBalanceAfter = (await t1.balanceOf(user)).toNumber();
    const t0PoolBalanceAfter = (await t0.balanceOf(pool.address)).toNumber();
    const t1PoolBalanceAfter = (await t1.balanceOf(pool.address)).toNumber();

    assert.isAbove(t0PoolBalanceBefore, t0PoolBalanceAfter);
    assert.isAbove(t1PoolBalanceBefore, t1PoolBalanceAfter);

    assert.isAbove(lpUserBalanceBefore, lpUserBalanceAfter);

    assert.isAbove(t0UserBalanceAfter, t0UserBalanceBefore);
    assert.equal(t0UserBalanceAfter, t0UserBalanceBefore + t0PoolBalanceBefore - t0PoolBalanceAfter);

    assert.isAbove(t1UserBalanceAfter, t1UserBalanceBefore);
    assert.equal(t1UserBalanceAfter, t1UserBalanceBefore + t1PoolBalanceBefore - t1PoolBalanceAfter);
}

describe('Flow', () => {
    it('Simulate', async () => {
        const accounts = await web3.eth.getAccounts();

        const [ldoOwner, inchOwner, daiOwner, stEthOwner, stEthDaiPoolOwner, rewardManagerOwner, liquidityProvider] = accounts;

        const ldoToken = await deployToken("Lido DAO Token", "LDO", 250000, ldoOwner);
        const inchToken = await deployToken("1INCH Token", "INCH", 250000, inchOwner);
        const daiToken = await deployToken("DAI Token", "DAI", 10000, daiOwner);
        const stEthToken = await deployToken("stETH Token", "stETH", 10000, stEthOwner);
        const [stEthDaiPool, rewardsContract] = await deployPoolAndRewards(
            stEthDaiPoolOwner,
            stEthToken,
            daiToken,
            inchToken,
            inchOwner,
            100000,     // Not sure about this
            10          // Not sure about this
        );

        const rewardManager = await deployRewardsManager(rewardManagerOwner, 1, rewardsContract, ldoToken);

        /**
         * Not sure about last params:
         * - Here may be a dependence on `block.timestamp` for `duration`.
         * - Need to figure out how `scale` is actually used in computations.
         */
        await rewardsContract.addGift(ldoToken.address, 100000, rewardManager.address, 10, { from: stEthDaiPoolOwner });

        /**
         * Actions that should be triggered by Aragon voting.
         * Particularly, starting next reward period and dispatching reward tokens.
         */
        await startNextRewardPeriod(rewardManager, ldoToken, ldoOwner, 200000, rewardsContract);

        /**
         * Give user 2K DAI and 2K stETH tokens.
         */
        await giveTokens(daiToken, daiOwner, liquidityProvider, 2000);
        await giveTokens(stEthToken, stEthOwner, liquidityProvider, 2000);

        /**
         * Put user's DAI and stETH tokens to liquidity pool (provide liquidity).
         * Pool evaluates amount of tokens to receive, base on some "fair" rules.
         * It does not take all amount, but takes something between min/max of each token from accepted pair.
         * This should guarantee that pool token-to-token balance is not radically changed.
         *
         * User received LP tokens in reward.
         */
        await provideLiquidityToPool(liquidityProvider, stEthDaiPool, stEthToken, daiToken, [1500, 1500], [1000, 1000]);

        /**
         * User stakes obtained LP tokens to rewards contract.
         */
        await stakeToRewards(liquidityProvider, stEthDaiPool, rewardsContract);

        /**
         * User exits from rewarding program by withdrawing all of the LP tokens.
         */
        await exitFromRewards(liquidityProvider, stEthDaiPool, rewardsContract);

        /**
         * User withdraws LP tokens from liquidity pool.
         */
        await withdrawLiquidityFromPool(liquidityProvider, stEthDaiPool, stEthToken, daiToken);
    });
});
