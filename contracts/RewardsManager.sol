// SPDX-License-Identifier: MIT

pragma solidity ^0.6.12;

/// Using OpenZeppelin 3.2.0
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/// @title FarmingRewards interface
/// @dev Interface for necessary methods of FarmingRewards contract
interface IFarmingRewards {
    function notifyRewardAmount(uint i, uint256 reward) external;
    function tokenRewards(uint i) external view returns(address, uint256, uint256, address, uint256, uint256, uint256, uint256);
}

/// @title Lido-1inch RewardsManager
contract RewardsManager is Ownable {
    /// @notice ERC20 tokens successfully recovered
    /// @param token Token contract address
    /// @param amount Amount of tokens recovered
    /// @param owner New token owner's address
    event ERC20TokenRecovered(address token, uint amount, address owner);

    /// @notice Gift identifier
    uint public giftIndex;
    /// @notice FarmingRewards contract address
    address public rewardsContract;
    /// @notice Reward token address
    address public rewardToken = 0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32;


    /// @notice Constructor
    /// @param _giftIndex Gift identifier
    /// @param _rewardsContract FarmingRewards contract address
    constructor(uint _giftIndex, address _rewardsContract, address _rewardToken) public {
        require(_rewardsContract != address(0));

        giftIndex = _giftIndex;
        rewardsContract = _rewardsContract;

        if (_rewardToken != address(0)) {
            rewardToken = _rewardToken;
        }
    }

    /// @notice Sets FarmingRewards contract address
    /// @dev This method is to ensure that RewardsManager is not depending on deployment order. 
    /// If deployment scheme is known and FarmingRewards is deployed before RewardsManager, 
    /// it can be inlined into a constructor.
    /// @param _rewardsContract FarmingRewards contract address
    function setRewardsContract(address _rewardsContract) public onlyOwner {
        require(_rewardsContract != address(0));

        rewardsContract = _rewardsContract;
    }

    /// @notice Checks if reward period is finished
    /// @return True if finished, false if not
    function is_reward_period_finished() public view returns (bool) {
        return block.timestamp >= _getPeriodFinish();
    }

    /// @notice Returns reward period finish date
    /// @return Timestamp of reward period finish date
    function out_of_funding_date() public view returns (uint) {
        return _getPeriodFinish();
    }

    /// @notice Start next reward period
    function start_next_rewards_period() public {
        uint amount = IERC20(rewardToken).balanceOf(address(this));

        require(amount > 0, "Rewards disabled");
        require(is_reward_period_finished(), "Rewards period not finished");
        require(IERC20(rewardToken).transfer(rewardsContract, amount), "Unable to transfer reward tokens");

        IFarmingRewards(rewardsContract).notifyRewardAmount(giftIndex, amount);
    }

    /// @notice Sends tokens to contract owner's address in emergency
    /// @param _tokenAddress Token address
    /// @param _amount Amount of tokens to recover
    function recover_erc20(address _tokenAddress, uint _amount) public onlyOwner {
        require(_tokenAddress != address(0));

        uint balance = IERC20(_tokenAddress).balanceOf(address(this));

        require(_amount <= balance, "Unable to recover tokens");
        require(IERC20(_tokenAddress).transfer(owner(), _amount), "Unable to transfer tokens");

        emit ERC20TokenRecovered(_tokenAddress, _amount, owner());
    }

    /// @notice Gets reward period finish date from FarmingRewards contract
    /// @return Timestamp of reward period finish date    
    function _getPeriodFinish() private view returns (uint) {
        (,,,,uint _periodFinish,,,) = IFarmingRewards(rewardsContract).tokenRewards(giftIndex);

        return _periodFinish;
    }
}
