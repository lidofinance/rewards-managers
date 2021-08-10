const StubERC20 = artifacts.require("StubERC20");
const RewardsManager = artifacts.require("RewardsManager");
const DummyContract = artifacts.require("Dummy");
const truffleAssert = require('truffle-assertions');

contract('RewardsManager', async (accounts) => {

    const [contractsOwner, otherAccount] = accounts;
    var token;
    var dummy;
    var rewardsManager;
	
	before(async function () {
    	token = await StubERC20.new("Lido DAO Token", "LDO", 250000, { from: contractsOwner });
		dummy = await DummyContract.new({ from: contractsOwner });
    	rewardsManager = await RewardsManager.new(1, dummy.address, token.address, { from: contractsOwner });
	});

    it('Owner can set RewordsContract address', async function () {
    	const newAddr = "0xa355B4B904ce09Bd1847f4cf133769BC0dfBC51B";
    	truffleAssert.passes(rewardsManager.setRewardsContract(newAddr), { from: contractsOwner });
    });

    it('Other account cannot set RewordsContract address', async function () {
    	const newAddr = "0xa355B4B904ce09Bd1847f4cf133769BC0dfBC51B";
    	truffleAssert.fails(rewardsManager.setRewardsContract(newAddr), { from: otherAccount });
    });

});
