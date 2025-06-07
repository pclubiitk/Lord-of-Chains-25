// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.7.0 <0.9.0;

contract Ordering 
{
    enum Status {Factory, Warehouse, Reserved, DeliveryBoy, Delivered}
    enum OrderStatus {Pending, Delivered, Cancelled}

    struct Transact {
        Status from;
        Status to;
        uint256 transactTime;
    }

    uint nextPid = 0;
    struct Product {
        string name;
        uint pid;
        Status status;
        Transact[] log;
        bool reserved;
        uint reservedOrderId;
    }

    mapping(uint => Product) public products;

    address public seller;
    constructor() 
    {
        seller = msg.sender;
    }

    uint nextOrderId = 0;
    struct Order 
    {
        uint orderId;
        uint[] products;
        uint256 deadline;
        uint256 orderTime;
        OrderStatus delivered;
    }

    mapping(uint => Order) public orders;

    address public warehouse;
    address public deliveryBoy;
    address public buyer;

    modifier onlySeller() 
    {
        require(msg.sender == seller, "Not the seller");
        _;
    }

    modifier onlyWarehouse() 
    {
        require(msg.sender == warehouse, "Not the warehouse");
        _;
    }

    modifier onlyDeliveryBoy() 
    {
        require(msg.sender == deliveryBoy, "Not the delivery boy");
        _;
    }

    modifier onlyBuyer() 
    {
        require(msg.sender == buyer, "Not the buyer");
        _;
    }

    event WarehouseSet(address warehouse);
    event DeliveryBoySet(address deliveryBoy);
    event BuyerSet(address buyer);
    event ProductTransferred(uint pid, string from, string to);
    event CreateProduct(address seller, string _name, uint nextPid);
    event OrderPlaced(address, uint);
    event DeadlineMissed(uint orderId, uint deadline, uint deliveredAt);

    // Seller sets warehouse address once
    function setWarehouse(address _warehouse) external onlySeller 
    {
        require(_warehouse != address(0), "Bad address");
        warehouse = _warehouse;
        emit WarehouseSet(_warehouse);
    }

    // Seller sets delivery boy address once
    function setDeliveryBoy(address _deliveryBoy) external onlySeller 
    {
        require(_deliveryBoy != address(0), "Bad address");
        deliveryBoy = _deliveryBoy;
        emit DeliveryBoySet(_deliveryBoy);
    }

    // Seller sets buyer address once
    function setBuyer(address _buyer) external onlySeller 
    {
        require(_buyer != address(0), "Bad address");
        buyer = _buyer;
        emit BuyerSet(_buyer);
    }

    function createProduct(string memory _name) public onlySeller 
    {
        Product storage p = products[nextPid];
        p.name = _name;
        p.pid = nextPid;
        p.status = Status.Factory;
        p.reserved = false;
        p.reservedOrderId = 0;
        emit CreateProduct(seller, _name, nextPid);
        nextPid++;
    }

    function viewProducts() public view returns (uint[] memory, string[] memory, string[] memory, bool[] memory) 
    {
        uint[] memory pids = new uint[](nextPid);
        string[] memory names = new string[](nextPid);
        string[] memory statuses = new string[](nextPid);
        bool[] memory reservedStates = new bool[](nextPid);
        for (uint i = 0; i < nextPid; i++) {
            pids[i] = products[i].pid;
            names[i] = products[i].name;
            statuses[i] = getStatusString(products[i].status);
            reservedStates[i] = products[i].reserved;
        }
        return (pids, names, statuses, reservedStates);
    }

    function getProductHistory(uint pid) public view returns (Transact[] memory) 
    {
        require(pid < nextPid, "Invalid product ID");
        return products[pid].log;
    }

    function getStatusString(Status currentStatus) public pure returns (string memory) 
    {
        if (currentStatus == Status.Factory) return "Factory";
        if (currentStatus == Status.Warehouse) return "Warehouse";
        if (currentStatus == Status.Reserved) return "Reserved";
        if (currentStatus == Status.DeliveryBoy) return "DeliveryBoy";
        if (currentStatus == Status.Delivered) return "Delivered";
        return "Unknown";
    }

    function placeOrder(uint[] memory _products) public onlyBuyer 
    {
        for (uint i = 0; i < _products.length; i++) {
            uint pid = _products[i];
            require(pid < nextPid, "Invalid product ID");
            require(
                products[pid].status == Status.Factory ||
                products[pid].status == Status.Warehouse,
                "Product not available for ordering"
            );
            require(!products[pid].reserved, "Product already reserved in another order");
            products[pid].status = Status.Reserved;
            products[pid].reserved = true;
            products[pid].reservedOrderId = nextOrderId;
        }
        orders[nextOrderId] = Order({
            orderId: nextOrderId,
            products: _products,
            deadline: block.timestamp + 5 * 60,
            orderTime: block.timestamp,
            delivered: OrderStatus.Pending
        });
        emit OrderPlaced(buyer, nextOrderId);
        nextOrderId++;
    }

    function viewOrders() public view returns (uint[] memory, OrderStatus[] memory) 
    {
        uint[] memory ids = new uint[](nextOrderId);
        OrderStatus[] memory statuses = new OrderStatus[](nextOrderId);
        for (uint i = 0; i < nextOrderId; i++) {
            ids[i] = orders[i].orderId;
            statuses[i] = orders[i].delivered;
        }
        return (ids, statuses);
    }

    function viewUndeliveredOrders() public view returns (uint[] memory) 
    {
        uint count = 0;
        for (uint i = 0; i < nextOrderId; i++) {
            if (orders[i].delivered == OrderStatus.Pending) count++;
        }
        uint[] memory ids = new uint[](count);
        uint j = 0;
        for (uint i = 0; i < nextOrderId; i++) {
            if (orders[i].delivered == OrderStatus.Pending) ids[j++] = orders[i].orderId;
        }
        return (ids);
    }

    // Seller -> Warehouse 
    function transferToWarehouse(uint orderId) public onlySeller 
    {
        require(orderId < nextOrderId, "Invalid order ID");
        require(orders[orderId].delivered == OrderStatus.Pending, "Order already delivered");

        for (uint i = 0; i < orders[orderId].products.length; i++) {
            uint pid = orders[orderId].products[i];

            // Only move if Reserved and reserved for this order
            if (products[pid].status == Status.Reserved && products[pid].reservedOrderId == orderId) 
            {
                products[pid].status = Status.Warehouse;
                products[pid].reserved = false;
                products[pid].reservedOrderId = 0;
                products[pid].log.push(Transact({
                    from: Status.Reserved,
                    to: Status.Warehouse,
                    transactTime: block.timestamp
                }));

                emit ProductTransferred(
                    pid,
                    getStatusString(Status.Reserved),
                    getStatusString(Status.Warehouse)
                );
            }
        }
    }

    // Warehouse -> DeliveryBoy 
    function transferToDeliveryBoy(uint orderId) public onlyWarehouse 
    {
        require(orderId < nextOrderId, "Invalid order ID");
        require(orders[orderId].delivered == OrderStatus.Pending, "Order already delivered");

        for (uint i = 0; i < orders[orderId].products.length; i++) 
        {
            uint pid = orders[orderId].products[i];
            require(products[pid].status == Status.Warehouse, "Not in warehouse");

            products[pid].status = Status.DeliveryBoy;
            products[pid].log.push(Transact({
                from: Status.Warehouse,
                to: Status.DeliveryBoy,
                transactTime: block.timestamp
            }));

            emit ProductTransferred(
                pid,
                getStatusString(Status.Warehouse),
                getStatusString(Status.DeliveryBoy)
            );
        }
    }

    // DeliveryBoy -> Buyer asserting deadline otherwise return to Warehouse
    function deliverToBuyer(uint orderId) public onlyDeliveryBoy 
    {
        require(orderId < nextOrderId, "Invalid order ID");
        require(orders[orderId].delivered == OrderStatus.Pending, "Order already delivered");

        if (block.timestamp <= orders[orderId].deadline) 
        {
            // Deliver all products in the order
            for (uint i = 0; i < orders[orderId].products.length; i++) 
            {
                uint pid = orders[orderId].products[i];
                require(products[pid].status == Status.DeliveryBoy, "Not with delivery boy");
                products[pid].status = Status.Delivered;
                products[pid].log.push(Transact({
                    from: Status.DeliveryBoy,
                    to: Status.Delivered,
                    transactTime: block.timestamp
                }));

                emit ProductTransferred(
                    pid,
                    getStatusString(Status.DeliveryBoy),
                    getStatusString(Status.Delivered)
                );
            }
            orders[orderId].delivered = OrderStatus.Delivered;
        } else {
            // Return all products to warehouse if deadline passed and unreserve
            for (uint i = 0; i < orders[orderId].products.length; i++) 
            {
                uint pid = orders[orderId].products[i];
                require(products[pid].status == Status.DeliveryBoy, "Not with delivery boy");
                products[pid].status = Status.Warehouse;
                products[pid].reserved = false;
                products[pid].reservedOrderId = 0;
                products[pid].log.push(Transact({
                    from: Status.DeliveryBoy,
                    to: Status.Warehouse,
                    transactTime: block.timestamp
                }));

                emit ProductTransferred(
                    pid,
                    getStatusString(Status.DeliveryBoy),
                    getStatusString(Status.Warehouse)
                );
            }
            orders[orderId].delivered = OrderStatus.Cancelled;
            emit DeadlineMissed(orderId, orders[orderId].deadline, block.timestamp);
        }
    }
}