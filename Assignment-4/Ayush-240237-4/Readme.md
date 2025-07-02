# Auction Smart Contract

A Solidity-based **NFT auction smart contract** that allows users to register, place bids, and win a unique NFT, with all logic for auction lifecycle and bidder management. Built using OpenZeppelin Contracts for ERC721 and ownership functionality.

---

## Features

- **NFT Minting**: The contract mints an ERC721 NFT for the auction winner.
- **Auction Lifecycle**: Owner can start, end, or cancel the auction.
- **Bidder Registration**: Users must register and pay a fee before bidding.
- **Bidding Logic**: Enforces minimum bid value and increments; tracks highest bid.
- **Refunds**: Losing bidders are refunded automatically when the auction ends or is canceled.
- **Owner Withdrawals**: Owner can withdraw contract balance after auction ends.
- **Metadata Support**: NFT metadata (token URI) is set for each minted NFT.

---

**Compile the contract** using your preferred Solidity tool.

---

## Usage

### 1. **Deploy the Contract**

Deploy with the following parameters:
- `initialOwner`: Address of the contract owner.
- `_minValue`: Minimum bid value (in wei).
- `_minIncreament`: Minimum increment for each new bid (in wei).
- `_BidDuration`: Auction duration (in seconds).
- `SetRegestrationFees`: Registration fee for bidders (in wei).
- `_auctionTokenURI`: Metadata URI for the NFT.

### 2. **Start the Auction**

The owner calls `Start()` to begin the auction.

### 3. **Bidder Registration**

Users must call `RegesterBidder()` and pay the registration fee.

### 4. **Place Bids**

Registered users call `CommitBid()` with their bid amount.

### 5. **End or Cancel Auction**

- Owner can call `End()` after time expires to finalize and mint NFT to the winner.
- Owner can call `Cancel()` to abort and refund all bidders.

### 6. **Withdraw Funds**

After the auction ends, the owner can call `WithDraw()` to collect proceeds.

---
