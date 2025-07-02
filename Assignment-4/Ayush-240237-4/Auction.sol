// SPDX-License-Identifier: MIT
// Compatible with OpenZeppelin Contracts ^5.0.0
pragma solidity ^0.8.27;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {ERC721URIStorage} from "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract Auction is ERC721, ERC721URIStorage, Ownable {

    enum Status{NotStarted,Started, Ended, Cancelled}

    Status public status;
    struct BidderData{
        uint data;
        uint applyFees;
    }

    address payable _owner = payable(msg.sender);
    mapping(address=>BidderData) private BidderSearch;
    uint private highest_bid;
    address payable private highest_bidder;
    uint private Fees;
    uint public minValue;
    uint public minIncreament;
    uint public BidDuration;
    uint public endTime;
    string public auctionTokenURI;
    address[] private bidders;
    uint private tokenCounter = 1;

    constructor(address initialOwner, uint _minValue,
     uint _minIncreament,
      uint _BidDuration,
       uint SetRegestrationFees,
       string memory _auctionTokenURI
       )
        ERC721("Auction", "AUC")
        Ownable(initialOwner)
    {
        minIncreament = _minIncreament;
        minValue = _minValue;
        Fees = SetRegestrationFees;
        BidDuration = _BidDuration;
        auctionTokenURI = _auctionTokenURI;
    }

    function safeMint(address to, uint256 tokenId, string memory uri)
        public
        onlyOwner
    {
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
    }

    // The following functions are overrides required by Solidity.

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
    // OpenZepplin Code ends here

    

    

    modifier _onlyOwner(){
        require (_owner== msg.sender,"Ownable: caller is not the owner");
        _;
    }

    function Start() public _onlyOwner {
        require(status == Status.NotStarted , "Auction has been started ");
        status = Status.Started;
        endTime = block.timestamp+BidDuration;
    }
   

    function Cancel() payable public _onlyOwner{
        require(status == Status.Started , "Auction has not started yet ");
        status = Status.Cancelled;
         for (uint i = 0; i < bidders.length; i++) {
            address bidder = bidders[i];
          
                uint amount = BidderSearch[bidder].data;
                payable(bidder).transfer(amount);
                BidderSearch[bidder].data = 0; 
            
        }
    }

     function End() payable public onlyOwner {
        require(block.timestamp >= endTime, "Auction ongoing");
        require(status == Status.Started, "Auction not running");
        status = Status.Ended;
        
        // Mint NFT to winner
         // Mint NFT to winner WITH METADATA
        _safeMint(highest_bidder, tokenCounter);
        _setTokenURI(tokenCounter, auctionTokenURI);  // Set metadata here
        tokenCounter++;

        
        // Refund all losing bidders
        for (uint i = 0; i < bidders.length; i++) {
            address bidder = bidders[i];
            if (bidder != highest_bidder) {
                uint amount = BidderSearch[bidder].data;
                payable(bidder).transfer(amount);
                BidderSearch[bidder].data = 0; // Prevent re-entrancy
            }
        }
    }
    
    function CommitBid() payable public{
        require(block.timestamp<= endTime , "Auction has ended");
        require(status == Status.Started , "Auction has not started yet ");
        if (block.timestamp >= endTime) {
        End();
        return;
    }
        require(BidderSearch[msg.sender].applyFees != 0, "Already registered");
        require(BidderSearch[msg.sender].applyFees==Fees, "Please Pay the Fees");

        require(BidderSearch[msg.sender].data+msg.value>highest_bid, "You should bid higher than the previous bidder");
        if (BidderSearch[payable(msg.sender)].data==0){
            require(msg.value > minValue, "Bids must be greater than the minimum value");
        }
        else {
            require(msg.value>=minIncreament, "You must make a higher bid");
        }
        BidderSearch[payable(msg.sender)] = BidderData(BidderSearch[msg.sender].data+msg.value, BidderSearch[msg.sender].applyFees); //BidderSearch[msg.sender].data
        highest_bidder = payable(msg.sender);
        highest_bid = msg.value;
    }

    function RegesterBidder() payable public{
         require(BidderSearch[msg.sender].applyFees!=Fees, "Already Regestered");
        if (BidderSearch[msg.sender].applyFees!= Fees){
           
            bidders.push(msg.sender);
            require(msg.value== Fees,"Pay the full Fee");
        BidderSearch[payable(msg.sender)] = BidderData(BidderSearch[msg.sender].data, BidderSearch[msg.sender].applyFees+msg.value);

        }
        
    }

    function WithDraw() _onlyOwner public{
        require(status == Status.Ended , "Auction has not ended yet ");
        payable(_owner).transfer(address(this).balance);
    
    }

    

    

}
