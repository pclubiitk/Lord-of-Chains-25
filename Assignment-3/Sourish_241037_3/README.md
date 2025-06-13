# SupplyNFT Smart Contract

## Overview

`SupplyNFT` is an ERC721-based smart contract built using OpenZeppelin Contracts. It represents a supply chain tracking system where products are minted as NFTs and transferred through various roles such as Seller, Warehouse, Delivery, and Buyer. Each transfer is auditable, and deadlines are enforced for delivery verification.

## Features

- ERC721-compliant NFT minting and URI storage
- Role-based access control (Seller, Warehouse, Delivery, Buyer)
- Audit logging with transfer timestamps and notes
- Delivery deadline tracking
- Temperature-sensitive package checks
- Transfer limits per role (max 5 transfers per role)

## Roles

There are four roles involved in the supply chain:
- **Seller**: Initiates the NFT minting for a product
- **Warehouse**: Receives packages from Seller (only accepts cold products)
- **Delivery**: Delivers to Buyer (only for cold products)
- **Buyer**: Final recipient of the package

Each address must be assigned a role using the `userRoles` mapping.

## Package Lifecycle

1. Seller mints an NFT using `mintProductNFT`.
2. Package can be transferred sequentially to Warehouse → Delivery → Buyer using `transferToNextRole`.
3. Each transfer requires a non-empty audit note and obeys the role-based logic.
4. Delivery time is compared against the 120-second deadline set at minting.

## Key Functions

### `mintProductNFT(string memory _tokenURI, bool isCold)`

- Mints a new product NFT.
- Sets a delivery deadline 120 seconds from creation.
- Marks if the package is temperature-sensitive.
- Only callable by addresses with `Seller` role.

### `transferToNextRole(uint _id, string memory auditNote)`

- Transfers the package to the next role in the chain.
- Validates role, audit note, and role-specific limits.
- Emits events for tracking.

### `getRole(uint _id)`

- Returns the current role of the specified package in string format.

### `checkDeadline(uint _id)`

- Checks if the package was delivered on time or is late.

## Events

- `PackageTransferred(uint id, string auditNote, Role prevRole, Role curRole, uint time)`
- `DeliveryStatus(uint id, string status, uint time)`

## Limits

Each role has a transfer cap of 5 to simulate operational constraints:
- Max 5 packages from Seller to Warehouse
- Max 5 cold packages from Warehouse to Delivery
- Max 5 deliveries to Buyer

## Deployment

The contract uses OpenZeppelin Contracts ^5.0.0 and should be deployed with an initial owner address.

```solidity
constructor(address initialOwner) ERC721("MyToken", "MTK") Ownable(initialOwner) {}