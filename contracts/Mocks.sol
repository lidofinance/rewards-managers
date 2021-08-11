// SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.6.12;

import './Vendor.sol';

contract StubERC20 is ERC20 {
    constructor(string memory name_, string memory symbol_, uint totalSupply_) ERC20(name_, symbol_) public {
        _mint(msg.sender, totalSupply_);
    }
}

contract StubFarmingRewards {
    uint public periodFinish;

    uint private _tokenRewards;
    uint private _giftIndex;

    constructor(uint tokenRewards_, uint giftIndex_, uint periodFinish_) public {
        _tokenRewards = tokenRewards_;
        _giftIndex = giftIndex_;
        periodFinish = periodFinish_;
    }

    function notifyRewardAmount(uint, uint256) public {}
    
    function tokenRewards(uint) public view returns(address, uint256, uint256, address, uint256, uint256, uint256, uint256) {
        return (address(0), 1, 1, address(0), periodFinish, 1, 1, 1);
    }
}
