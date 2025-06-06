# SupplyChainTracker Smart Contract

A Solidity-based supply chain tracking system that models the lifecycle of a package from a seller to a buyer, involving a warehouse and a delivery boy. This smart contract ensures transparency, timing constraints, and traceability in package delivery on the Ethereum blockchain.

---

## Features

- **Roles & Access Control**
  - `buyer`, `seller`, `warehouse`, and `deliveryBoy` are predefined addresses.
  - Only designated roles can trigger respective package movement functions.

- **Package Lifecycle**
  - Create a package (`AtSeller`)
  - Transfer to `InWarehouse`
  - Move to `WithDeliveryBoy`
  - Finally delivered to the `buyer` (`Delivered`)

- **Timing Constraints**
  - A package has a strict 2-minute (`120 seconds`) delivery deadline.
  - Auto-cancel feature if the deadline is missed at any stage.

- **Traceability**
  - Complete transaction history is recorded for each package.
  - Current status can be queried anytime.

---

## Contract Overview

### Roles
- `buyer`: Deployer of the contract (`msg.sender`)
- `seller`: Initialized as a fixed address (can be updated using `registerAsSeller()`)
- `warehouse`: Fixed address
- `deliveryBoy`: Fixed address

### Basic Structures

#### Package
- `id`: Unique identifier
- `name`: Name/label of the item
- `currentHolder`: Address currently holding the package
- `location`: Enum representing current state
- `deadline`: Delivery deadline (2 minutes from creation)
- `isCancelled`: Tracks if package is cancelled

#### TransferRecord
- Logs each transfer with:
  - `from` address
  - `to` address
  - `timestamp` of the event

---


