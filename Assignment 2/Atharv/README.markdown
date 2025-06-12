# Supply Chain Smart Contract Function Explanation

This document provides a simplified explanation of the functions in the `SupplyChain.sol` smart contract for the Supply Chain Based E-Commerce System.

## Functions

- **Constructor**  
  Initializes the contract by assigning addresses for the four roles: warehouse, delivery boy, buyer, and seller.

- **addProduct**  
  Allows the seller to add a new product with a specified name. Assigns a unique ID to the product and sets the seller as its initial holder.

- **createRequest**  
  Enables the buyer to request a product by its ID, specifying a delivery time window (e.g., 1 hour from the current time).

- **createPackage**  
  Permits the seller to fulfill a buyer's request by creating a package for the requested product, setting its expected delivery time based on the request.

- **transferProduct**  
  Allows the current holder (seller, warehouse, delivery boy, or buyer) to transfer the product to another role. Logs the timestamp and new holder. When transferred to the buyer, marks the product as delivered and checks if it was on time.

- **viewTransactionHistory**  
  Allows anyone to view a product's transfer history, returning a list of all holders and timestamps of transfers.

- **checkDeliveryStatus**  
  Returns whether a delivered product arrived within its expected delivery time window.

- **getTimestamp**  
  Returns the current block timestamp, used for tracking time within the contract.

## Purpose
These functions enable transparent tracking of a product's journey through the supply chain, enforce role-based access, and verify delivery timelines using blockchain technology.
