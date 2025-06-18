# ProductOrderNFT: ERC721 Supply Chain Tracking System

## Overview

**ProductOrderNFT** is a robust ERC721-based smart contract for tracking products through a supply chain using NFTs. It enforces a strict product path (Seller ➝ Warehouse ➝ Delivery ➝ Buyer), supports temperature-sensitive goods, expiry and delivery deadlines, and provides a full audit trail via on-chain events and role-based access control.

---

## Getting Started

### 1. Prerequisites

- Solidity ^0.8.27
- OpenZeppelin Contracts (AccessControl, ERC721URIStorage)
- Remix IDE or Hardhat/Foundry for deployment
- MetaMask wallet with testnet ETH

---

### 2. Deployment

1. **Clone or copy the contract code into Remix or your preferred IDE.**
2. **Compile** with Solidity version 0.8.27.
3. **Deploy** the contract, passing four addresses for the roles:
   - Seller
   - Warehouse
   - Delivery
   - Buyer

---

### 3. Minting a Product NFT

Call `safeMint` with:
- `to`: Seller address
- `tokenId`: Unique product ID
- `uri`: IPFS or HTTPS link to product metadata JSON
- `isTemperatureSensitive`: `true` or `false`
- `expiryTimestamp`: Unix timestamp (e.g., 1767225600 for 2025-12-31)
- `deliveryDeadline`: Unix timestamp for expected delivery

---


### 5. Metadata JSON Example

```json
{
  "name": "Coke",
  "description": "Chilled drink for summer. Expires on 2025-12-31.",
  "image": "https://copper-worthy-eagle-590.mypinata.cloud/ipfs/bafybeifr2sbvto6mbgyvy56qdad7nateyrucmlt63v22ugk2pb2szj2lpu",
  "attributes": [
    {
      "trait_type": "Temperature Sensitive",
      "value": "Yes"
    },
    {
      "trait_type": "Expiry Date",
      "display_type": "date",
      "value": 1767225600 
    },
    {
      "trait_type": "Delivery Deadline",
      "display_type": "date",
      "value": 1750357800 
    },
    {
      "trait_type": "Manufacturer",
      "value": "Coca Cola"
    },
    {
      "trait_type": "Batch ID",
      "value": "A125"
    }
  ]
}
```

---

### 6. Events

- `ProductTransfer(tokenId, fromRole, toRole, timestamp)`: Emitted on every transfer.
- `ProductExpired(tokenId, timestamp)`: Emitted if a product is expired at any stage.
- `DeliveryStatus(tokenId, "OnTime"/"Delayed", timestamp)`: Emitted on delivery to buyer, indicating if on time.

---

### 7. Access Control

- Only addresses with the correct role can call each transfer function.
- Use `grantRole` and `hasRole` to manage and verify roles.

---

## Troubleshooting

- **Role Errors:** Ensure your MetaMask is set to the correct address for the role you are trying to use.
- **Transfer Fails:** Check product status, expiry, and temperature sensitivity requirements.
- **Events Not Visible:** Use a block explorer or Remix’s logs to view emitted events.

---

