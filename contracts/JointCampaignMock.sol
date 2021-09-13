// SPDX-License-Identifier: MIT

pragma solidity 0.5.16;

pragma experimental ABIEncoderV2;

import {JointCampaign} from "./arcx_contracts/staking/JointCampaign.sol";

contract JointCampaignMock is JointCampaign {
  function isMinter(
        address _user,
        uint256 _amount,
        uint256 _positionId
    )
        public
        view
        returns (bool)
    {
        return true;
    }
}
