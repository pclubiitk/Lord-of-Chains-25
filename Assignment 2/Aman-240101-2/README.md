# SupplyChain

## Overview

`SupplyChain` is a Solidity smart contract designed to log the journey of a product through a four-stage supply chain:

1. Seller (deployer)
2. Warehouse
3. Delivery Boy
4. Buyer

Each product receives a unique ID when the Buyer requests it. The Seller then sets a delivery window (measured in seconds), and the contract stores an on-chain deadline (`block.timestamp + window`). Every handoff (Seller → Warehouse → Delivery Boy → Buyer) is recorded in a history array along with the timestamp. Once the Delivery Boy hands off to the Buyer, the contract marks the product as delivered and emits an event indicating whether delivery was on time.

No funds change hands in this contract—it only serves as an audit trail. Anyone can inspect a product’s transfer history or verify on-time status.

---

## Deployed Contract Address


*0xac9B2E3C479B3D965C58f02643d3472100F5F9a4*

---

## File Structure

- `SupplyChainTracker.sol`  
  Contains the full Solidity implementation. Copy this file into Remix to compile and deploy.

- `README.md`  
  (This file.) Explains how the contract works, how to interact with it in Remix.

---

## Usage (Remix)

1. **Open Remix**  
   Navigate to [https://remix.ethereum.org](https://remix.ethereum.org).

2. **Add Contract**  
   - Click the “+” icon in the File Explorer panel and name the new file `supply_chain.sol`.  
   - Paste the contents of `supply_chain.sol` into that file.

3. **Compile**  
   - Select the **Solidity Compiler** tab.  
   - Choose compiler version `0.8.19` (or any `0.8.x`).  
   - Click **Compile supply_chain.sol**.

4. **Deploy**  
   - Switch to the **Deploy & Run Transactions** tab.  
   - For **Environment**, select **Injected Web3** (for MetaMask/testnet).  
   - Click **Deploy** (no constructor arguments needed).  
   - Once deployed, you will see an entry under “Deployed Contracts,” showing:  
     ```
     SupplyChainTracker at 0x1234…ABCD
     ```  

5. **Assign Roles**  
   (All three calls must be made from the Seller account—the deployer.)

   1. `setWarehouse(<warehouse_address>)`  
   2. `setDeliveryBoy(<delivery_boy_address>)`  
   3. `setBuyer(<buyer_address>)`  

   Each function takes a single `address` argument and emits an event confirming the assignment.

6. **Track a Product**  
   1. **Buyer →**  
      - Switch to the Buyer account.  
      - Call `requestProduct()`. This returns a `productId` (e.g., `1`).  
   2. **Seller →**  
      - Switch back to the Seller account.  
      - Call `createProduct(productId, deliveryWindowSeconds)`. For example:  
        ```js
        createProduct(1, 3600) 
        ```  
      - This records Seller → Warehouse and sets the on-chain deadline.  
   3. **Warehouse →**  
      - Switch to the Warehouse account.  
      - Call `transferToDelivery(productId)`.  
      - This records Warehouse → Delivery Boy.  
   4. **Delivery Boy →**  
      - Switch to the Delivery Boy account.  
      - Call `transferToBuyer(productId)`.  
      - This records Delivery Boy → Buyer, marks `delivered = true`, and emits `ProductDelivered(productId, onTime)`.  
   5. **Inspect On-Chain Data**  
      - `viewTransactionHistory(productId)` returns an array of all `TransferRecord` entries (from, to, timestamp).  
      - `checkOnTime(productId)` returns `true` if final handoff occurred on or before the deadline, else `false`.  
      - `getProductDetails(productId)` returns basic data:  
        - `id`  
        - `expectedDeliveryTime` (timestamp)  
        - `delivered` (boolean)  
        - `historyLength` (number of handoff records)

---

## Example Sequence

Assume Remix accounts:

- Seller:   `0xAAA0000000000000000000000000000000000001`  
- Warehouse:`0xBBB0000000000000000000000000000000000002`  
- Delivery Boy: `0xCCC000000000000000000000000000000000003`  
- Buyer:    `0xDDD0000000000000000000000000000000000004`  

```text
// As Seller (deployer):
setWarehouse(0xBBB0000000000000000000000000000000000002)
setDeliveryBoy(0xCCC0000000000000000000000000000000000003)
setBuyer(0xDDD0000000000000000000000000000000000004)

// Switch to Buyer:
requestProduct()       → returns 1

// Switch to Seller:
createProduct(1, 3600) // 1-hour window

// Switch to Warehouse:
transferToDelivery(1)

// Switch to Delivery Boy:
transferToBuyer(1)

// Any account:
viewTransactionHistory(1)
checkOnTime(1)
