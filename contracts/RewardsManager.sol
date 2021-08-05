// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0 <0.9.0;

// @title Lido-1inch RewardsManager

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

interface IFarmingRewards {

    struct TokenRewards {
        IERC20 gift;
        uint256 scale;
        uint256 duration;
        address rewardDistribution;
        uint256 periodFinish;
        uint256 rewardRate;
        uint256 lastUpdateTime;
        uint256 rewardPerTokenStored;
        mapping(address => uint256) userRewardPerTokenPaid;
        mapping(address => uint256) rewards;
    }

    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function lastTimeRewardApplicable(uint i) external view returns (uint256);
    function rewardPerToken(uint i) external view returns (uint256);
    function earned(uint i, address account) external view returns (uint256);
    function getReward(uint i) external;
    function getAllRewards() external;
    function notifyRewardAmount(uint i, uint256 reward) external;
    function setRewardDistribution(uint i, address _rewardDistribution) external;
    function setDuration(uint i, uint256 duration) external;
    function setScale(uint i, uint256 scale) external;
    function addGift(IERC20 gift, uint256 duration, address rewardDistribution, uint256 scale) external;
    function name() external view returns(string memory);
    function symbol() external view returns(string memory);
    function decimals() external view returns(uint8);
    function stake(uint256 amount) external;
    function withdraw(uint256 amount) external;
    function exit() external;
    function fee() external view returns(uint256);
    function slippageFee() external view returns(uint256);
    function decayPeriod() external view returns(uint256);
    function feeVotes(address user) external view returns(uint256);
    function slippageFeeVotes(address user) external view returns(uint256);
    function decayPeriodVotes(address user) external view returns(uint256);
    function feeVote(uint256 vote) external;
    function slippageFeeVote(uint256 vote) external;
    function decayPeriodVote(uint256 vote) external;
    function discardFeeVote() external;
    function discardSlippageFeeVote() external;
    function discardDecayPeriodVote() external;
    function rescueFunds(IERC20 token, uint256 amount) external;
}

contract RewardsManager is Ownable, Pausable {

	uint giftIndex = 0;
	address public rewardsContract;
	IERC20 public LDOToken = 0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32;

	constructor(uint _giftIndex, address _rewardsContract) {
		giftIndex = _giftIndex;
		rewardsContract = _rewardsContract;
	}

	function isRewardPeriodFinished() public view returns (uint periodFinish) {
		periodFinish = IFarmingRewards(rewardsContract).tokenRewards(giftIndex)[3];
	}

}


