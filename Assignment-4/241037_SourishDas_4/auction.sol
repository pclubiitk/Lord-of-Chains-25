// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract TimeBasedAuction is ERC721URIStorage, Ownable {
    uint256 public applicationFee = 0.01 ether;
    uint256 public bidAmount = 1 ether;
    uint256 public startTime;
    uint256 public endTime;
    bool public auctionEnded;
    bool public nftMinted;
    address public winner;
    uint256 private tokenIdCounter;

    struct Bid {
        uint256 hashedBid;
        bool revealed;
        uint256 actualBid;
    }

    mapping(address => Bid) private bids;
    address[] private bidders;
    uint256 private highestBid;

    constructor(uint256 _biddingDuration) ERC721("AuctionWinnerNFT", "AWNFT") Ownable(msg.sender) {
    startTime = block.timestamp;
    endTime = block.timestamp + _biddingDuration;
    }


    modifier onlyDuringBidding() {
        require(block.timestamp >= startTime && block.timestamp <= endTime, "Bidding is closed");
        _;
    }

    modifier onlyAfterAuction() {
        require(block.timestamp > endTime, "Auction not ended");
        _;
    }

    function applyAndBid(uint256 _hashedBid) external payable onlyDuringBidding {
        require(msg.value == applicationFee + bidAmount, "Incorrect amount sent");
        require(bids[msg.sender].hashedBid == 0, "Already applied");

        bids[msg.sender].hashedBid = _hashedBid;
        bidders.push(msg.sender);
    }

    function revealBid(uint256 _actualBid, string memory _secret) external onlyAfterAuction {
        Bid storage bid = bids[msg.sender];
        require(!bid.revealed, "Already revealed");
        require(bid.hashedBid == uint256(keccak256(abi.encodePacked(_actualBid, _secret))), "Hash mismatch");

        bid.revealed = true;
        bid.actualBid = _actualBid;

        if (_actualBid > highestBid) {
            highestBid = _actualBid;
            winner = msg.sender;
        }
    }

    function endAuctionAndDistribute() external onlyOwner onlyAfterAuction {
        require(!auctionEnded, "Auction already ended");

        auctionEnded = true;

        if (winner != address(0) && !nftMinted) {
            _safeMint(winner, tokenIdCounter);
            _setTokenURI(tokenIdCounter, "ipfs://Qm..."); // Replace with actual IPFS URI
            tokenIdCounter++;
            nftMinted = true;
        }

        payable(owner()).transfer(address(this).balance);
    }

    function getMyBidStatus() external view returns (bool, uint256) {
        return (bids[msg.sender].revealed, bids[msg.sender].actualBid);
    }

    function getWinner() external view onlyOwner onlyAfterAuction returns (address) {
        return winner;
    }

    function getContractBalance() external view onlyOwner returns (uint256) {
        return address(this).balance;
    }
}
