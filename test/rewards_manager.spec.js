const truffleAssert = require('truffle-assertions');

const StubERC20 = artifacts.require("StubERC20");
const StubFarmingRewards = artifacts.require("StubFarmingRewards");
const RewardsManager = artifacts.require("RewardsManager");

const zeroAddress = "0x0000000000000000000000000000000000000000";
const timeInThePast = 1628687598;

function debug(name, val) {
    console.log(name, val, typeof(val));
}

contract('RewardsManager', async (accounts) => {
    const [contractsOwner, otherAccount] = accounts;
    const tokenRewards = 100;
    const giftIndex = 1;

    let token;
    let rewards;
    let rewardsManager;

    before(async () => {
        token = await StubERC20.new("Lido DAO Token", "LDO", 250000, { from: contractsOwner });
        rewards = await StubFarmingRewards.new(tokenRewards, giftIndex, timeInThePast, { from: contractsOwner });
        rewardsManager = await RewardsManager.new(giftIndex, rewards.address, token.address, { from: contractsOwner });
    });

    it('Constructor: public varialbles set', async () => {
        assert.equal(await rewardsManager.giftIndex(), giftIndex, "giftIndex should match");
        assert.equal(await rewardsManager.rewardsContract(), rewards.address, "rewardsContract address should match");
        assert.equal(await rewardsManager.rewardToken(), token.address, "token address should match");
    });

    it('Constructor: rewards contract zero address reverted', async () => {
        await truffleAssert.fails(RewardsManager.new(giftIndex, zeroAddress, token.address, { from: contractsOwner }));
    });

    it('out_of_funding_date', async () => {
        const outOfFundingDate = (await rewardsManager.out_of_funding_date()).toNumber();

        assert.equal(outOfFundingDate, timeInThePast, "out_of_funding_date should match");
    });

    it('is_reward_period_finished: in the past', async () => {
        const currentBlockTimestamp = (await web3.eth.getBlock(await web3.eth.getBlockNumber())).timestamp;
        const periodFinish = (await rewards.periodFinish()).toNumber();
        const is_reward_period_finished = await rewardsManager.is_reward_period_finished();

        assert.equal(is_reward_period_finished, currentBlockTimestamp >= periodFinish, "currentBlockTimestamp is less than periodFinish");
    });

    it('is_reward_period_finished: in the future', async () => {
        const currentBlockTimestamp = (await web3.eth.getBlock(await web3.eth.getBlockNumber())).timestamp;
        const timeInTheFuture = currentBlockTimestamp + 1314000;

        const rewardsLocal = await StubFarmingRewards.new(tokenRewards, giftIndex, timeInTheFuture, { from: contractsOwner });
        const rewardsManagerLocal = await RewardsManager.new(giftIndex, rewardsLocal.address, token.address, { from: contractsOwner });

        const periodFinish = (await rewardsLocal.periodFinish()).toNumber();
        const isRewardPeriodFinished = await rewardsManagerLocal.is_reward_period_finished();

        assert.equal(isRewardPeriodFinished, currentBlockTimestamp >= periodFinish, "currentBlockTimestamp is more than or equal to periodFinish");
    });

    it('start_next_rewards_period: token amount = 0', async () => {
        await truffleAssert.fails(rewardsManager.start_next_rewards_period({ from: contractsOwner }), truffleAssert.ErrorType.REVERT, "Rewards disabled");
    });

    it('start_next_rewards_period: token amount > 0, rewards period not finished', async () => {
        const currentBlockTimestamp = (await web3.eth.getBlock(await web3.eth.getBlockNumber())).timestamp;
        const timeInTheFuture = currentBlockTimestamp + 1314000;

        const tokenLocal = await StubERC20.new("Lido DAO Token", "LDO", 250000, { from: contractsOwner });
        const rewardsLocal = await StubFarmingRewards.new(tokenRewards, giftIndex, timeInTheFuture, { from: contractsOwner });
        const rewardsManagerLocal = await RewardsManager.new(giftIndex, rewardsLocal.address, tokenLocal.address, { from: contractsOwner });

        await tokenLocal.transfer(rewardsManagerLocal.address, tokenRewards, { from: contractsOwner });

        await truffleAssert.fails(rewardsManagerLocal.start_next_rewards_period({ from: contractsOwner }), truffleAssert.ErrorType.REVERT, "Rewards period not finished");
    });

    it('start_next_rewards_period: token amount > 0, unable to transfer tokens', async () => {
        await token.transfer(rewardsManager.address, tokenRewards, { from: contractsOwner });

        await truffleAssert.fails(rewardsManager.start_next_rewards_period({ from: contractsOwner, gas: 21000 }));
    });

    it('start_next_rewards_period: passes', async () => {
        await truffleAssert.passes(rewardsManager.start_next_rewards_period({ from: contractsOwner }));
    });

    it('setRewardsContract: owner can set rewards contract address', async () => {
        const newAddr = "0xa355B4B904ce09Bd1847f4cf133769BC0dfBC51B";

        await truffleAssert.passes(rewardsManager.setRewardsContract(newAddr, { from: contractsOwner }));

        assert.equal((await rewardsManager.rewardsContract()).valueOf(), newAddr, "rewardsContract address should match");
    });

    it('setRewardsContract: other account cannot set rewards contract address', async () => {
        const newAddr = "0xa355B4B904ce09Bd1847f4cf133769BC0dfBC51B";

        await truffleAssert.fails(rewardsManager.setRewardsContract(newAddr, { from: otherAccount }));
    });
});
