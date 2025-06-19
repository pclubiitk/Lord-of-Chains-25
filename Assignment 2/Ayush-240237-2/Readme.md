# SupplyChainTracker Smart Contract
A Solidity smart contract for tracking products through a supply chain, from seller to buyer, with role-based access and delivery time validation.
---

## Overview

**SupplyChainTracker** is a smart contract designed to manage and track the movement of products through a supply chain. It enforces a strict sequence of transfers between four roles: Seller, Warehouse, DeliveryBoy, and Buyer. The contract records every transfer, validates delivery times, and provides transparency for all participants.

---

## Roles

- **Seller**: The contract deployer, responsible for creating products.
- **Warehouse**: Receives products from the seller and passes them to the delivery boy.
- **DeliveryBoy**: Delivers products from the warehouse to the buyer.
- **Buyer**: Requests products and receives final delivery.

---

## Contract Deployment

Deploy the contract by specifying the addresses for the warehouse, delivery boy, and buyer:

```solidity
SupplyChainTracker(address _warehouse, address _deliveryBoy, address _buyer)
```

The deployer becomes the seller.

---

## Usage Guide

### 1. Buyer Request Creation

The buyer initiates a request for a product:

```solidity
createBuyerRequest(uint256 requestId)
```
- Only callable by the buyer.
- Registers a request for a product with a unique `requestId`.

### 2. Product Creation

The seller creates a product in response to a buyer request:

```solidity
createProduct(uint256 productId, uint256 expectedDeliveryTime, uint256 requestId)
```
- Only callable by the seller.
- `expectedDeliveryTime` must be a future timestamp.
- Links the product to the buyer's request.

### 3. Product Transfer

Products must be transferred in the following sequence:

1. Seller → Warehouse
2. Warehouse → DeliveryBoy
3. DeliveryBoy → Buyer

Each transfer is performed by the current holder:

```solidity
transferProduct(uint256 productId, Role to)
```
- Only the current holder can transfer to the next role.
- Enforces correct transfer order.

### 4. Querying Product Status

- **Get transfer history:**
  ```solidity
  getTransferHistory(uint256 productId)
  ```
  Returns an array of all transfers for the product.

- **Check if delivery was on time:**
  ```solidity
  isDeliveryOnTime(uint256 productId)
  ```
  Returns `true` if delivered to the buyer before the expected delivery time.

- **Get current holder:**
  ```solidity
  getCurrentStatus(uint256 productId)
  ```
  Returns the current role holding the product.

---

## Events

- `ProductCreated(productId, buyer, expectedTime)`: Emitted when a product is created.
- `ProductTransferred(productId, from, to, timestamp)`: Emitted on every product transfer.
- `BuyerRequestCreated(requestId, buyer)`: Emitted when a buyer request is made.

---

## Security

- **Role enforcement**: Only authorized addresses can perform actions for their role.
- **Transfer sequence**: Transfers must follow the defined order.
- **Existence checks**: Functions validate product and request existence before proceeding.

---
