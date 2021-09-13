# @version 0.2.12
# @license MIT

from vyper.interfaces import ERC20

token: public(address)
weekMerkleRoots: public(HashMap[uint256, bytes32])


@external
def __init__(_token: address):
    self.token = _token


@external
def seedAllocations(_week: uint256, _merkleRoot: bytes32, _totalAllocation: uint256):
    self.weekMerkleRoots[_week] = _merkleRoot
    assert ERC20(self.token).transferFrom(msg.sender, self, _totalAllocation), "ERR_TRANSFER_FAILED"