// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SupplyChainTracker {
    enum Role { Seller, Warehouse, DeliveryBoy, Buyer }
    
    struct Transfer {
        Role from;
        Role to;
        uint256 timestamp;
    }
    
    struct Product {
        uint256 id;
        uint256 expectedDeliveryTime;
        Role currentHolder;
        Transfer[] transferHistory;
        address buyer;
        bool exists;
    }
    
    address public seller;
    address public warehouse;
    address public deliveryBoy;
    address public buyer;
    
    mapping(uint256 => Product) public products;
    mapping(uint256 => address) public buyerRequests;
    
    event ProductCreated(uint256 indexed productId, address indexed buyer, uint256 expectedTime);
    event ProductTransferred(uint256 indexed productId, Role indexed from, Role indexed to, uint256 timestamp);
    event BuyerRequestCreated(uint256 indexed requestId, address indexed buyer);

    modifier onlyRole(Role _role) {
        require(
            (_role == Role.Seller && msg.sender == seller) ||
            (_role == Role.Warehouse && msg.sender == warehouse) ||
            (_role == Role.DeliveryBoy && msg.sender == deliveryBoy) ||
            (_role == Role.Buyer && msg.sender == buyer),
            "Unauthorized role"
        );
        _;
    }

    constructor(address _warehouse, address _deliveryBoy, address _buyer) {
        seller = msg.sender;
        warehouse = _warehouse;
        deliveryBoy = _deliveryBoy;
        buyer = _buyer;
    }

    function createBuyerRequest(uint256 _requestId) external onlyRole(Role.Buyer) {
        buyerRequests[_requestId] = msg.sender;
        emit BuyerRequestCreated(_requestId, msg.sender);
    }

    function createProduct(uint256 _productId, uint256 _expectedDeliveryTime, uint256 _requestId) 
        external 
        onlyRole(Role.Seller) 
    {
        require(buyerRequests[_requestId] != address(0), "No buyer request found");
        require(!products[_productId].exists, "Product already exists");
        require(_expectedDeliveryTime > block.timestamp, "Invalid delivery window");

        // Create the product struct WITHOUT initializing the array
        products[_productId].id = _productId;
        products[_productId].expectedDeliveryTime = _expectedDeliveryTime;
        products[_productId].currentHolder = Role.Seller;
        products[_productId].buyer = buyerRequests[_requestId];
        products[_productId].exists = true;
        // transferHistory array is empty at this point

        // Now push the initial transfer to the storage array
        products[_productId].transferHistory.push(Transfer(
            Role.Seller,
            Role.Seller,
            block.timestamp
        ));
        
        emit ProductCreated(_productId, buyerRequests[_requestId], _expectedDeliveryTime);
    }

    function transferProduct(uint256 _productId, Role _to) external {
        Product storage product = products[_productId];
        require(product.exists, "Product does not exist");
        
        Role currentRole = product.currentHolder;
        require(
            (currentRole == Role.Seller && _to == Role.Warehouse && msg.sender == seller) ||
            (currentRole == Role.Warehouse && _to == Role.DeliveryBoy && msg.sender == warehouse) ||
            (currentRole == Role.DeliveryBoy && _to == Role.Buyer && msg.sender == deliveryBoy),
            "Invalid transfer sequence"
        );

        product.transferHistory.push(Transfer(
            currentRole,
            _to,
            block.timestamp
        ));
        
        product.currentHolder = _to;
        emit ProductTransferred(_productId, currentRole, _to, block.timestamp);
    }

    function getTransferHistory(uint256 _productId) 
        external 
        view 
        returns (Transfer[] memory) 
    {
        require(products[_productId].exists, "Product does not exist");
        uint256 length = products[_productId].transferHistory.length;
        Transfer[] memory history = new Transfer[](length);
        for (uint256 i = 0; i < length; i++) {
            history[i] = products[_productId].transferHistory[i];
        }
        return history;
    }

    function isDeliveryOnTime(uint256 _productId) external view returns (bool) {
        Product storage product = products[_productId];
        require(product.exists, "Product does not exist");
        require(product.currentHolder == Role.Buyer, "Product not delivered yet");
        
        uint256 deliveryTime = product.transferHistory[product.transferHistory.length - 1].timestamp;
        return deliveryTime <= product.expectedDeliveryTime;
    }

    function getCurrentStatus(uint256 _productId) external view returns (Role) {
        require(products[_productId].exists, "Product does not exist");
        return products[_productId].currentHolder;
    }
}
