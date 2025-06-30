// SPDX-License-Identifier: MIT
// Compatible with OpenZeppelin Contracts ^5.0.0
pragma solidity ^0.8.27;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {ERC721URIStorage} from "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract Auction is ERC721, ERC721URIStorage, Ownable {
    uint256 private _nextTokenId;

    uint public ownr;
    uint private highestBidder;
    uint private highestBid;
    uint private endTime;
    uint public startTime;
    
    // Fixed application fee (non-refundable)
    uint public constant APPLICATION_FEE = 0.01 ether;
    


    bool public started;
    bool private ended;

    event HighestBidIncreased();
    event AuctionEnded(uint winner, uint amount);

    modifier onlyOwnr(uint role) {
        require(role == ownr, "Not auction owner");
        _;
    }

    // Modifier to automatically end auction if time is up
    modifier autoEnd() {
        if (started && !ended && block.timestamp >= endTime) {
            _endAuction();
        }
        _;
    }

    constructor()
        ERC721("MyToken", "MTK")
        Ownable(msg.sender)
    {
        ownr = 0;
        highestBid = 0;
        startTime = block.timestamp;
    }

    function safeMint(address to, string memory uri)
        internal
        onlyOwner
        returns (uint256)
    {
        uint256 tokenId = _nextTokenId++;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        return tokenId;
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }

    function startAuction(uint Timelimit, uint role) public onlyOwnr(role) {
        require(!started, "Auction already started");
        started = true;
        endTime = block.timestamp + Timelimit;
    }

    function bid(uint role) public payable autoEnd {
        require(started, "Auction not started yet");
        require(!ended, "Auction ended");
        require(msg.value > highestBid + APPLICATION_FEE, "Bid too low (must exceed highest bid + application fee)");
        
        // Calculate actual bid amount (total - application fee)
        uint bidAmount = msg.value - APPLICATION_FEE;
        
        // Automatically refund previous highest bidder (only their bid amount, not the fee)
        if (highestBid > 0) {
            payable(msg.sender).transfer(highestBid);
        }

        highestBidder = role;
        highestBid = bidAmount;

        emit HighestBidIncreased();
    }

    // Internal function to end auction automatically
    function _endAuction() internal {
        require(started && !ended, "Invalid auction state");
        
        ended = true;
        
        // Mint NFT to contract owner (they can transfer to winner)
        safeMint(owner(), "https://turquoise-voluntary-mosquito-398.mypinata.cloud/ipfs/bafkreia6zod6jpnpansfhv23vgnunuldrevc6qo4dhc42gybk3yazcbdzq");
        
        emit AuctionEnded(highestBidder, highestBid);
        
        // Automatic withdrawal - transfer all funds to owner
        uint contractBalance = address(this).balance;
        if (contractBalance > 0) {
            payable(owner()).transfer(contractBalance);
        }
    }

    // Manual end function (in case no one calls autoEnd)
    function endAuction(uint role) public onlyOwnr(role) {
        require(block.timestamp >= endTime, "Auction still ongoing");
        _endAuction();
    }

    // Automatic withdraw function - drains contract to owner
    function withdraw() public {
        require(ended, "Auction must be ended first");
        uint contractBalance = address(this).balance;
        require(contractBalance > 0, "No funds to withdraw");
        payable(owner()).transfer(contractBalance);
    }

    // Restricted visibility - only basic auction status
    function isAuctionActive() public view returns (bool) {
        return started && !ended && block.timestamp < endTime;
    }

    // No functions to view bids or bidder details for privacy
}