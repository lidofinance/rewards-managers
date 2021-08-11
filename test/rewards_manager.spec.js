const StubERC20 = artifacts.require("StubERC20");
const StubFarmingRewards = artifacts.require("StubFarmingRewards");
const RewardsManager = artifacts.require("RewardsManager");
const truffleAssert = require('truffle-assertions');
const zero_address = "0x0000000000000000000000000000000000000000";
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

    beforeEach(async () => {
        token = await StubERC20.new("Lido DAO Token", "LDO", 250000, { from: contractsOwner });
        rewards = await StubFarmingRewards.new(tokenRewards, giftIndex, timeInThePast, { from: contractsOwner });
        rewardsManager = await RewardsManager.new(giftIndex, rewards.address, token.address, { from: contractsOwner });
    });

    it('Constructor: Public varialbles set', async () => {
        assert.equal(await rewardsManager.giftIndex(), giftIndex, "giftIndex should match");
        assert.equal(await rewardsManager.rewardsContract(), rewards.address, "rewardsContract address should match");
        assert.equal(await rewardsManager.rewardToken(), token.address, "token address should match");
    });

    it('out_of_funding_date', async () => {
        const result = (await rewardsManager.out_of_funding_date()).toNumber();
        assert.equal(result, timeInThePast, "out_of_funding_date should match");
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

        rewards = await StubFarmingRewards.new(tokenRewards, giftIndex, timeInTheFuture, { from: contractsOwner });
        rewardsManager = await RewardsManager.new(giftIndex, rewards.address, token.address, { from: contractsOwner });

        const periodFinish = (await rewards.periodFinish()).toNumber();
        const is_reward_period_finished = await rewardsManager.is_reward_period_finished();

        assert.equal(is_reward_period_finished, currentBlockTimestamp >= periodFinish, "currentBlockTimestamp is more than or equal to periodFinish");
    });

    it('setRewardsContract: Owner can set rewards contract address', async () => {
        const newAddr = "0xa355B4B904ce09Bd1847f4cf133769BC0dfBC51B";

        truffleAssert.passes(rewardsManager.setRewardsContract(newAddr), { from: contractsOwner });
        assert.equal((await rewardsManager.rewardsContract()).valueOf(), rewards.address, "rewardsContract address should match");
    });

    it('setRewardsContract: Other account cannot set rewards contract address', async () => {
        const newAddr = "0xa355B4B904ce09Bd1847f4cf133769BC0dfBC51B";

        truffleAssert.fails(rewardsManager.setRewardsContract(newAddr), { from: otherAccount });
    });

});

// !!!! WIP
// contract('Rewards contract address check', async (accounts) => {
//     const [contractsOwner, otherAccount] = accounts;
//     const tokenRewards = 100;
//     const giftIndex = 1;

//     let token;
//     let rewards;
//     let rewardsManager;

//     beforeEach(async () => {
//         token = await StubERC20.new("Lido DAO Token", "LDO", 250000, { from: contractsOwner });
//     });

//     it('Rewards contract address not null reverted', async () => {
//         truffleAssert.fails(await RewardsManager.new(giftIndex, zero_address, token.address), { from: contractsOwner });
//     });

// });
