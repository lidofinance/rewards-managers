// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0 <0.9.0;

// @title Lido-1inch RewardsManager

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract RewardsManager is Ownable {

	uint giftIndex = 0;
	address public rewardsContract;
	ERC20 public LDOToken = 0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32;

	constructor(uint _giftIndex, address _rewardsContract) {
		giftIndex = _giftIndex;
		rewardsContract = _rewardsContract;
	}

}
