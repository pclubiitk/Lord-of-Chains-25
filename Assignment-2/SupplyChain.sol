pragma solidity ^0.8.0;

contract SupplyChain {
    // Roles
    address public warehouse;
    address public deliveryBoy;
    address public buyer;
    address public seller;

    // Structs
    struct Product {
        uint256 id;
        string name;
        address currentHolder;
        uint256 expectedDeliveryTime;
        bool isDelivered;
        uint256[] transferTimestamps;
        address[] transferHolders;
    }

    struct Request {
        uint256 productId;
        uint256 expectedDeliveryTime;
        bool isFulfilled;
    }

    // Mappings
    mapping(uint256 => Product) public products;
    mapping(uint256 => Request) public requests;
    uint256 public productCounter;
    uint256 public requestCounter;

    // Events
    event ProductAdded(uint256 indexed productId, string name, address seller);
    event RequestCreated(uint256 indexed requestId, uint256 productId, address buyer, uint256 expectedDeliveryTime);
    event PackageCreated(uint256 indexed productId, address buyer, uint256 expectedDeliveryTime);
    event ProductTransferred(uint256 indexed productId, address from, address to, uint256 timestamp);
    event DeliveryStatus(uint256 indexed productId, bool isOnTime);

    // Modifiers
    modifier onlyWarehouse() {
        require(msg.sender == warehouse, "Only warehouse can call this function");
        _;
    }

    modifier onlyDeliveryBoy() {
        require(msg.sender == deliveryBoy, "Only delivery boy can call this function");
        _;
    }

    modifier onlyBuyer() {
        require(msg.sender == buyer, "Only buyer can call this function");
        _;
    }

    modifier onlySeller() {
        require(msg.sender == seller, "Only seller can call this function");
        _;
    }

    constructor(address _warehouse, address _deliveryBoy, address _buyer, address _seller) {
        warehouse = _warehouse;
        deliveryBoy = _deliveryBoy;
        buyer = _buyer;
        seller = _seller;
        productCounter = 0;
        requestCounter = 0;
    }

    // Seller adds a product
    function addProduct(string memory _name) public onlySeller {
        productCounter++;
        products[productCounter] = Product({
            id: productCounter,
            name: _name,
            currentHolder: seller,
            expectedDeliveryTime: 0,
            isDelivered: false,
            transferTimestamps: new uint256[](0),
            transferHolders: new address[](0)
        });
        emit ProductAdded(productCounter, _name, seller);
    }

    // Buyer creates a request for a product
    function createRequest(uint256 _productId, uint256 _deliveryWindow) public onlyBuyer {
        require(products[_productId].id != 0, "Product does not exist");
        requestCounter++;
        requests[requestCounter] = Request({
            productId: _productId,
            expectedDeliveryTime: block.timestamp + _deliveryWindow,
            isFulfilled: false
        });
        emit RequestCreated(requestCounter, _productId, buyer, block.timestamp + _deliveryWindow);
    }

    // Seller creates a package based on buyer's request
    function createPackage(uint256 _requestId) public onlySeller {
        Request storage request = requests[_requestId];
        require(request.productId != 0, "Request does not exist");
        require(!request.isFulfilled, "Request already fulfilled");
        Product storage product = products[request.productId];
        product.expectedDeliveryTime = request.expectedDeliveryTime;
        request.isFulfilled = true;
        emit PackageCreated(request.productId, buyer, request.expectedDeliveryTime);
    }

    // Transfer product between roles
    function transferProduct(uint256 _productId, address _to) public {
        Product storage product = products[_productId];
        require(product.id != 0, "Product does not exist");
        require(!product.isDelivered, "Product already delivered");
        require(msg.sender == product.currentHolder, "Only current holder can transfer");
        require(_to == warehouse || _to == deliveryBoy || _to == buyer, "Invalid recipient");

        product.transferTimestamps.push(block.timestamp);
        product.transferHolders.push(_to);
        product.currentHolder = _to;

        // Check if delivered to buyer
        if (_to == buyer) {
            product.isDelivered = true;
            bool isOnTime = block.timestamp <= product.expectedDeliveryTime;
            emit DeliveryStatus(_productId, isOnTime);
        }

        emit ProductTransferred(_productId, msg.sender, _to, block.timestamp);
    }

    // View transaction history for a product
    function viewTransactionHistory(uint256 _productId) public view returns (address[] memory holders, uint256[] memory timestamps) {
        Product storage product = products[_productId];
        require(product.id != 0, "Product does not exist");
        return (product.transferHolders, product.transferTimestamps);
    }

    // Check if delivery is on time
    function checkDeliveryStatus(uint256 _productId) public view returns (bool) {
        Product storage product = products[_productId];
        require(product.id != 0, "Product does not exist");
        require(product.isDelivered, "Product not yet delivered");
        return block.timestamp <= product.expectedDeliveryTime;
    }

    // Get current block timestamp
    function getTimestamp() public view returns (uint256) {
        return block.timestamp;
    }
}