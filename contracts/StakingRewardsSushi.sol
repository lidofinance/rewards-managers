pragma solidity 0.5.17;

import "./StakingRewards.sol";

/// @notice Interface which any contract has to implement
/// to be used in MasterChefV2 contract as Rewarder
interface IRewarder {
    function onSushiReward(
        uint256 pid,
        address user,
        address recipient,
        uint256 sushiAmount,
        uint256 newLpAmount
    ) external;

    function pendingTokens(
        uint256 pid,
        address user,
        uint256 sushiAmount
    ) external view returns (IERC20[] memory, uint256[] memory);
}

/// @notice Slice of methods of MasterChefV2 contract used in StakingRewardsSushi contract
interface IMasterChefV2 {
    function lpToken(uint256 pid) external view returns (IERC20 _lpToken);
}

/// @notice Rewarder to be used in MasterChefV2 contract based on
/// Synthetix's StakingRewards contract
contract StakingRewardsSushi is StakingRewards, IRewarder {
    address public constant MASTERCHEF_V2 = 0xEF0881eC094552b2e128Cf945EF17a6752B4Ec5d;

    constructor(
        address _owner,
        address _rewardsDistribution,
        address _rewardsToken,
        address _stakingToken,
        uint256 _rewardsDuration
    )
        public
        StakingRewards(_owner, _rewardsDistribution, _rewardsToken, _stakingToken, _rewardsDuration)
    {}

    /// @notice Implements abstract methods from StakingRewards contract
    /// and returns total amount of staked tokens in the pool.
    /// @dev Instead of storing this value in standalone variable and update it
    /// when user balances updates, we can take this value from the stakingToken directly.
    function totalSupply() public view returns (uint256) {
        return stakingToken.balanceOf(MASTERCHEF_V2);
    }

    /// @notice Returns list of rewardTokens and list of corresponding earned rewards of user
    function pendingTokens(
        uint256,
        address user,
        uint256
    ) external view returns (IERC20[] memory _rewardTokens, uint256[] memory _rewardAmounts) {
        _rewardTokens = new IERC20[](1);
        _rewardTokens[0] = rewardsToken;
        _rewardAmounts = new uint256[](1);
        _rewardAmounts[0] = earned(user);
    }

    /// @notice Pays reward to user and updates balance of user when called by MasterChefV2 contract
    /// with correct pid value
    /// @dev On every call of this method StakingRewardsSushi will transfer earned tokens of user
    /// to passed recipient address.
    function onSushiReward(
        uint256 pid,
        address user,
        address recipient,
        uint256,
        uint256 newLpAmount
    ) external onlyMCV2 {
        require(IMasterChefV2(MASTERCHEF_V2).lpToken(pid) == stakingToken, "Wrong PID.");
        _payReward(user, recipient);
        _balances[user] = newLpAmount;
    }

    modifier onlyMCV2() {
        require(msg.sender == MASTERCHEF_V2, "Only MCV2 can call this function.");
        _;
    }
}
