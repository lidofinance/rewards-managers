pragma solidity 0.5.17;

import "./StakingRewards.sol";

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

interface IMasterChefV2 {
    function lpToken(uint256 pid) external view returns (IERC20 _lpToken);
}

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

    function totalSupply() public view returns (uint256) {
        return stakingToken.balanceOf(MASTERCHEF_V2);
    }

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
