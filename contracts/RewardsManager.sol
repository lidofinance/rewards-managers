// SPDX-License-Identifier: MIT

pragma solidity ^0.6.12;

// @title Lido-1inch RewardsManager

/// Using OpenZeppelin 3.2.0

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";

interface IFarmingRewards {

    function notifyRewardAmount(uint i, uint256 reward) external;
    function tokenRewards(uint i) external view returns(address, uint256, uint256, address, uint256, uint256, uint256, uint256);
}

contract RewardsManager is Ownable, Pausable {

    event ERC20TokenRecovered(address token, uint amount, address owner);

    uint public giftIndex;
    address public rewardsContract;
    address public rewardToken = 0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32;


    constructor(uint _giftIndex, address _rewardsContract) public {
        require(_rewardsContract != address(0));
        giftIndex = _giftIndex;
        rewardsContract = _rewardsContract;
    }

    function setRewardsContract(address _rewardsContract) public onlyOwner {
        require(_rewardsContract != address(0));
        rewardsContract = _rewardsContract;
    }

    function setTokenContract(address _tokenAddress) public onlyOwner {
        require(_tokenAddress != address(0));
        rewardToken = _tokenAddress;
    }

    function is_reward_period_finished() public view returns (bool) {
        return block.timestamp >= _getPeriodFinish();
    }

    function out_of_funding_date() public view returns (uint) {
        return _getPeriodFinish();
    }

    function start_next_rewards_period() public {
        uint amount = IERC20(rewardToken).balanceOf(address(this));
        require(amount > 0, "Rewards disabled");
        require(!is_reward_period_finished(), "Rewards period not finished");
        IERC20(rewardToken).approve(rewardsContract, amount);
        IFarmingRewards(rewardsContract).notifyRewardAmount(giftIndex, amount);
    }

    function recover_erc20(address _tokenAddress, uint _amount) public onlyOwner {
        require(_tokenAddress != address(0));
        uint balance = IERC20(_tokenAddress).balanceOf(address(this));
        require(_amount <= balance, "Unable to recover tokens");
        IERC20(_tokenAddress).transfer(owner(), _amount);
        emit ERC20TokenRecovered(_tokenAddress, _amount, owner());
    }

    function _getPeriodFinish() private view returns (uint) {
        (,,,,uint _periodFinish,,,) = IFarmingRewards(rewardsContract).tokenRewards(giftIndex);
        return _periodFinish;
    }

}


