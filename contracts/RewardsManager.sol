// SPDX-License-Identifier: MIT

pragma solidity ^0.6.12;

// @title Lido-1inch RewardsManager

/// Using OpenZeppelin 3.2.0

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";

abstract contract AFarmingRewards {

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

    TokenRewards[] public tokenRewards;

    function totalSupply() external view virtual returns (uint256);
    function balanceOf(address account) external view virtual returns (uint256);
    function lastTimeRewardApplicable(uint i) external view virtual returns (uint256);
    function rewardPerToken(uint i) external view virtual returns (uint256);
    function earned(uint i, address account) external view virtual returns (uint256);
    function getReward(uint i) external virtual;
    function getAllRewards() external virtual;
    function notifyRewardAmount(uint i, uint256 reward) external virtual;
    function setRewardDistribution(uint i, address _rewardDistribution) external virtual;
    function setDuration(uint i, uint256 duration) external virtual;
    function setScale(uint i, uint256 scale) external virtual;
    function addGift(IERC20 gift, uint256 duration, address rewardDistribution, uint256 scale) external virtual;
    function name() external view virtual returns(string memory);
    function symbol() external view virtual returns(string memory);
    function decimals() external view virtual returns(uint8);
    function stake(uint256 amount) virtual external;
    function withdraw(uint256 amount) virtual external;
    function exit() external virtual;
    function fee() external view virtual returns(uint256);
    function slippageFee() external view virtual returns(uint256);
    function decayPeriod() external view virtual returns(uint256);
    function feeVotes(address user) external view virtual returns(uint256);
    function slippageFeeVotes(address user) external view virtual returns(uint256);
    function decayPeriodVotes(address user) external view virtual returns(uint256);
    function feeVote(uint256 vote) external virtual;
    function slippageFeeVote(uint256 vote) external virtual;
    function decayPeriodVote(uint256 vote) external virtual;
    function discardFeeVote() external virtual;
    function discardSlippageFeeVote() external virtual;
    function discardDecayPeriodVote() external virtual;
    function rescueFunds(IERC20 token, uint256 amount) external virtual;
}

contract RewardsManager is Ownable, Pausable {

	event ERC20TokenRecovered(address token, uint amount, address owner);

	uint public giftIndex;
	address public rewardsContract;
	address public constant LDOToken = 0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32;


	constructor(uint _giftIndex, address _rewardsContract) public {
		require(_rewardsContract != address(0));
		giftIndex = _giftIndex;
		rewardsContract = _rewardsContract;
	}

	function setRewardsContract(address _rewardsContract) public onlyOwner {
		require(_rewardsContract != address(0));
		rewardsContract = _rewardsContract;
	}

	function isRewardPeriodFinished() public view returns (bool) {
		return block.timestamp >= _getPeriodFinish();
	}

	function outOfFundingDate() public view returns (uint) {
		return _getPeriodFinish();
	}

	function startNextRewardsPeriod() public {
		uint amount = IERC20(LDOToken).balanceOf(address(this));
		require(amount > 0, "Rewards disabled");
		require(!isRewardPeriodFinished(), "Rewards period not finished");
		IERC20(LDOToken).approve(rewardsContract, amount);
		AFarmingRewards(rewardsContract).notifyRewardAmount(giftIndex, amount);
	}

	function recoverERC20(address _tokenAddress, uint _amount) public onlyOwner {
		require(_tokenAddress != address(0));
		uint balance = IERC20(_tokenAddress).balanceOf(address(this));
		require(_amount <= balance);
		IERC20(_tokenAddress).transfer(owner(), _amount);
		emit ERC20TokenRecovered(_tokenAddress, _amount, owner());
	}

	function _getPeriodFinish() private view returns (uint) {
		uint _periodFinish;
		(,,,,_periodFinish,,,) = AFarmingRewards(rewardsContract).tokenRewards(giftIndex);
		return _periodFinish;
	}

}


