// SPDX-License-Identifier: MIT

pragma solidity 0.5.17;

import "./StakingRewards.sol";

contract StakingRewardsCurve is StakingRewards {
    /* ========== STATE VARIABLES ========== */
    uint256 private _totalSupply;

    /* ========== CONSTRUCTOR ========== */

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

    /* ========== VIEWS ========== */

    function totalSupply() public view returns (uint256) {
        return _totalSupply;
    }

    /* ========== MUTATIVE FUNCTIONS ========== */

    function stake(uint256 amount) external nonReentrant notPaused updateReward(msg.sender) {
        require(amount > 0, "Cannot stake 0");
        _totalSupply = _totalSupply.add(amount);
        _balances[msg.sender] = _balances[msg.sender].add(amount);
        stakingToken.safeTransferFrom(msg.sender, address(this), amount);
        emit Staked(msg.sender, amount);
    }

    function withdraw(uint256 amount) public nonReentrant updateReward(msg.sender) {
        require(amount > 0, "Cannot withdraw 0");
        _totalSupply = _totalSupply.sub(amount);
        _balances[msg.sender] = _balances[msg.sender].sub(amount);
        stakingToken.safeTransfer(msg.sender, amount);
        emit Withdrawn(msg.sender, amount);
    }

    function getReward() public {
        _payReward(msg.sender, msg.sender);
    }

    function exit() external {
        withdraw(_balances[msg.sender]);
        getReward();
    }
}
