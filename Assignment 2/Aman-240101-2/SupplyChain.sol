// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// On-chain tracker: Seller → Warehouse → DeliveryBoy → Buyer
contract SupplyChainTracker {
    address public seller;
    address public warehouse;
    address public deliveryBoy;
    address public buyer;

    uint256 public productCount;

    enum Role { None, Seller, Warehouse, DeliveryBoy, Buyer }

    struct TransferRecord {
        Role from;
        Role to;
        uint256 timestamp;
    }

    struct Product {
        uint256 id;
        uint256 expectedDeliveryTime;
        bool delivered;
        TransferRecord[] history;
    }

    mapping(uint256 => Product) private products;

    event WarehouseSet(address warehouse);
    event DeliveryBoySet(address deliveryBoy);
    event BuyerSet(address buyer);
    event ProductRequested(uint256 productId, address buyer, uint256 timestamp);
    event ProductCreated(uint256 productId, uint256 expectedDeliveryTime);
    event ProductTransferred(uint256 productId, Role from, Role to, uint256 timestamp);
    event ProductDelivered(uint256 productId, bool onTime);

    modifier onlySeller() {
        require(msg.sender == seller, "Only seller");
        _;
    }

    modifier onlyWarehouse() {
        require(msg.sender == warehouse, "Only warehouse");
        _;
    }

    modifier onlyDeliveryBoy() {
        require(msg.sender == deliveryBoy, "Only delivery boy");
        _;
    }

    modifier onlyBuyer() {
        require(msg.sender == buyer, "Only buyer");
        _;
    }

    constructor() {
        seller = msg.sender;
    }

    // Seller sets warehouse address once
    function setWarehouse(address _warehouse) external onlySeller {
        require(_warehouse != address(0), "Bad address");
        warehouse = _warehouse;
        emit WarehouseSet(_warehouse);
    }

    // Seller sets delivery boy address once
    function setDeliveryBoy(address _deliveryBoy) external onlySeller {
        require(_deliveryBoy != address(0), "Bad address");
        deliveryBoy = _deliveryBoy;
        emit DeliveryBoySet(_deliveryBoy);
    }

    // Seller sets buyer address once
    function setBuyer(address _buyer) external onlySeller {
        require(_buyer != address(0), "Bad address");
        buyer = _buyer;
        emit BuyerSet(_buyer);
    }

    // Buyer asks for a new product ID
    function requestProduct() external onlyBuyer returns (uint256) {
        productCount += 1;
        uint256 newId = productCount;
        products[newId].id = newId;
        emit ProductRequested(newId, msg.sender, block.timestamp);
        return newId;
    }

    // Seller creates product and logs Seller→Warehouse
    function createProduct(uint256 productId, uint256 deliveryWindowSeconds) external onlySeller {
        require(warehouse != address(0), "Warehouse not set");
        Product storage p = products[productId];
        require(p.id == productId, "Not requested");
        require(p.expectedDeliveryTime == 0, "Already created");

        p.expectedDeliveryTime = block.timestamp + deliveryWindowSeconds;
        p.history.push(TransferRecord({
            from: Role.Seller,
            to: Role.Warehouse,
            timestamp: block.timestamp
        }));

        emit ProductCreated(productId, p.expectedDeliveryTime);
        emit ProductTransferred(productId, Role.Seller, Role.Warehouse, block.timestamp);
    }

    // Warehouse hands off to DeliveryBoy
    function transferToDelivery(uint256 productId) external onlyWarehouse {
        require(deliveryBoy != address(0), "DeliveryBoy not set");
        Product storage p = products[productId];
        require(p.id == productId, "Invalid ID");
        require(p.expectedDeliveryTime != 0, "Not created");
        require(!p.delivered, "Already delivered");

        TransferRecord storage last = p.history[p.history.length - 1];
        require(last.to == Role.Warehouse, "Not at warehouse");

        p.history.push(TransferRecord({
            from: Role.Warehouse,
            to: Role.DeliveryBoy,
            timestamp: block.timestamp
        }));

        emit ProductTransferred(productId, Role.Warehouse, Role.DeliveryBoy, block.timestamp);
    }

    // DeliveryBoy hands off to Buyer and checks on-time
    function transferToBuyer(uint256 productId) external onlyDeliveryBoy {
        require(buyer != address(0), "Buyer not set");
        Product storage p = products[productId];
        require(p.id == productId, "Invalid ID");
        require(p.expectedDeliveryTime != 0, "Not created");
        require(!p.delivered, "Already delivered");

        TransferRecord storage last = p.history[p.history.length - 1];
        require(last.to == Role.DeliveryBoy, "Not with delivery boy");

        p.history.push(TransferRecord({
            from: Role.DeliveryBoy,
            to: Role.Buyer,
            timestamp: block.timestamp
        }));

        p.delivered = true;
        bool onTime = (block.timestamp <= p.expectedDeliveryTime);

        emit ProductTransferred(productId, Role.DeliveryBoy, Role.Buyer, block.timestamp);
        emit ProductDelivered(productId, onTime);
    }

    // Return all transfers for a product
    function viewTransactionHistory(uint256 productId)
        external
        view
        returns (TransferRecord[] memory)
    {
        Product storage p = products[productId];
        require(p.id == productId, "Invalid ID");
        return p.history;
    }

    // Check if final delivery was on time
    function checkOnTime(uint256 productId) external view returns (bool) {
        Product storage p = products[productId];
        require(p.id == productId, "Invalid ID");
        require(p.delivered, "Not delivered");

        TransferRecord storage last = p.history[p.history.length - 1];
        return (last.timestamp <= p.expectedDeliveryTime);
    }

    // Get basic product info
    function getProductDetails(uint256 productId)
        external
        view
        returns (
            uint256 id,
            uint256 expectedDeliveryTime,
            bool delivered,
            uint256 historyLength
        )
    {
        Product storage p = products[productId];
        require(p.id == productId, "Invalid ID");
        return (
            p.id,
            p.expectedDeliveryTime,
            p.delivered,
            p.history.length
        );
    }
}
