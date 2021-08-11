const StubERC20 = artifacts.require("StubERC20");
const StubFarmingRewards = artifacts.require("StubFarmingRewards");
const RewardsManager = artifacts.require("RewardsManager");
const truffleAssert = require('truffle-assertions');

contract('RewardsManager', async (accounts) => {
    const [contractsOwner, otherAccount] = accounts;
    const tokenRewards = 100;
    const giftIndex = 1;

    let token;
    let rewards;
    let rewardsManager;

    before(async () => {
        token = await StubERC20.new("Lido DAO Token", "LDO", 250000, { from: contractsOwner });
        rewards = await StubFarmingRewards.new(tokenRewards, giftIndex, { from: contractsOwner });
        rewardsManager = await RewardsManager.new(giftIndex, rewards.address, token.address, { from: contractsOwner });
    });

    it('Owner can set rewards contract address (setRewardsContract)', async () => {
        const newAddr = "0xa355B4B904ce09Bd1847f4cf133769BC0dfBC51B";

        truffleAssert.passes(rewardsManager.setRewardsContract(newAddr), { from: contractsOwner });
    });

    it('Other account cannot set rewards contract address (setRewardsContract)', async () => {
        const newAddr = "0xa355B4B904ce09Bd1847f4cf133769BC0dfBC51B";

        truffleAssert.fails(rewardsManager.setRewardsContract(newAddr), { from: otherAccount });
    });
});
