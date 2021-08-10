pragma solidity ^0.6.12;

import './Vendor.sol';

contract StubERC20 is ERC20 {
    constructor(string memory name_, string memory symbol_, uint totalSupply_) ERC20(name_, symbol_) public {
        _mint(msg.sender, totalSupply_);
    }
}

contract Dummy {

    uint private _tokenRewards;
    uint private _giftIndex;

    constructor(uint tokenRewards_, uint giftIndex_) public {
        _tokenRewards = tokenRewards_;
        _giftIndex = giftIndex_;
    }

    function notifyRewardAmount(uint i, uint256 reward) public {

    }
    
    function tokenRewards(uint i) public view returns(address, uint256, uint256, address, uint256, uint256, uint256, uint256) {
        return (address(0), 1, 1, address(0), 1, 1, 1, 1);
    }
}