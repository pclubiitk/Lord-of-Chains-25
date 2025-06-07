# Supply Chain Smart Contract

This repository contains the Solidity smart contract for the supply chain/order workflow implemented and tested on the Sepolia testnet.

## Deployed Contract Address

- **Sepolia Testnet Contract Address:**  
  `0x824aa10ca4906B91E2AaDc7b80343C30038D45ee`
   https://sepolia.etherscan.io/address/0x824aa10ca4906B91E2AaDc7b80343C30038D45ee
---

## Contract Function Signatures

Below are the main public/external functions available in the contract:

### Role Setup

- **function setWarehouse(address _warehouse) public onlySeller**
  - Registers the warehouse address (callable by the seller).

- **function setDeliveryBoy(address _deliveryBoy) public onlySeller**
  - Registers the delivery boy address (callable by the seller).

- **function setBuyer(address _buyer) public onlySeller**
  - Registers the buyer address (callable by the seller).

---

### Order Lifecycle

- **function placeOrder(string memory _name) public onlyBuyer**
  - Buyer places an order for a product.

- **function transferToWarehouse(uint _id) public onlySeller**
  - Seller transfers the product to the warehouse.

- **function transferToDeliveryBoy(uint _id) public onlyWarehouse**
  - Warehouse hands over the product to the delivery boy.

- **function deliverToBuyer(uint _id) public onlyDeliveryBoy**
  - Delivery boy delivers the product to the buyer.

---

### Product Query

- **function getProduct(uint _id) public view returns (Product memory)**
  - Returns details of a product by its ID.

- **function getDeadlineForProduct(uint _id) public view returns (uint)**
  - Returns the deadline timestamp for the current step of a product.

---

### State Variables

- **seller** — Address of the seller (deployer)
- **warehouse** — Address of the warehouse
- **deliveryBoy** — Address of the delivery boy
- **buyer** — Address of the buyer

---

## Submission Instructions

- Only the Solidity contract file (`SupplyChain.sol`) is included in this submission, as required.
