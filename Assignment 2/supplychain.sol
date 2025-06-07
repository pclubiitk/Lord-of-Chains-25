// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SupplyChainTracker {

    // Defining addresses
    address public buyer = msg.sender;
    address public seller = 0x3333333333333333333333333333333333333333;
    address public warehouse = 0x1111111111111111111111111111111111111111;
    address public deliveryBoy = 0x2222222222222222222222222222222222222222;

    enum Location {
        AtSeller,
        InWarehouse,
        WithDeliveryBoy,
        Delivered,
        Cancelled
    }

    // Defining complex structures
    struct Package {
        uint id;
        string name;
        address currentHolder;
        Location location;
        uint deadline;      
        bool isCancelled;
    }

    struct TransferRecord {
        address from;
        address to;
        uint timestamp;
    }

    // Defining mappings to store order packages mapped with their order IDs
    mapping(uint => Package) public packages;
    mapping(uint => TransferRecord[]) public packageTransfers;

    // Defining events
    event PackageTransferred(
        uint packageId,
        address from,
        address to,
        uint timestamp,
        Location newLocation,
        bool onTime
    );

    event PackageCancelled(
        uint packageId,
        string reason,
        uint timestamp
    );

    // Defining the modifiers to ensure sequential execution of the functions
    modifier onlySeller() {
        require(msg.sender == seller, "Not the seller");
        _;
    }

    modifier onlyWarehouse() {
        require(msg.sender == warehouse, "Not the warehouse");
        _;
    }

    modifier onlyDeliveryBoy() {
        require(msg.sender == deliveryBoy, "Not the delivery boy");
        _;
    }

    modifier onlyBuyer() {
        require(msg.sender == buyer, "Not the buyer");
        _;
    }

    modifier notCancelled(uint _id) {
        require(!packages[_id].isCancelled, "Package is cancelled");
        _;
    }

    // Function to change access to seller
    function registerAsSeller() public {
    seller = msg.sender;
    }

    // Function to create a package
    function createPackage(uint _id, string memory _name) public onlySeller {
        require(packages[_id].id == 0, "Package ID already used");
        uint deadline = block.timestamp + 120;

        packages[_id] = Package({
            id: _id,
            name: _name,
            currentHolder: seller,
            location: Location.AtSeller,
            deadline: deadline,
            isCancelled: false
        });
    }

    // Functions to transfer the package to different locations 
    function transferToWarehouse(uint _id) public onlySeller notCancelled(_id) {
        Package storage p = packages[_id];
        require(p.location == Location.AtSeller, "Package not at seller");
        require(block.timestamp <= p.deadline, "Deadline passed. Auto-cancelled.");
        _transfer(_id, warehouse, Location.InWarehouse);
    }

    function transferToDeliveryBoy(uint _id) public onlyWarehouse notCancelled(_id) {
        Package storage p = packages[_id];
        require(p.location == Location.InWarehouse, "Package not in warehouse");
        require(block.timestamp <= p.deadline, "Deadline passed. Auto-cancelled.");
        _transfer(_id, deliveryBoy, Location.WithDeliveryBoy);
    }

    function deliverToBuyer(uint _id) public onlyDeliveryBoy notCancelled(_id) {
        Package storage p = packages[_id];
        require(p.location == Location.WithDeliveryBoy, "Package not with delivery boy");
        require(block.timestamp <= p.deadline, "Deadline passed. Auto-cancelled.");
        _transfer(_id, buyer, Location.Delivered);
    }

    // Internal transfer function 
    function _transfer(uint _id, address _to, Location _newLocation) internal {
        Package storage p = packages[_id];
        address _from = p.currentHolder;

        p.currentHolder = _to;
        p.location = _newLocation;

        bool onTime = block.timestamp <= p.deadline;

        packageTransfers[_id].push(TransferRecord({
            from: _from,
            to: _to,
            timestamp: block.timestamp
        }));

        emit PackageTransferred(_id, _from, _to, block.timestamp, _newLocation, onTime);
    }

    function cancelIfLate(uint _id) public {
        Package storage p = packages[_id];
        require(!p.isCancelled, "Already cancelled");
        require(p.location != Location.Delivered, "Already delivered");

        if (block.timestamp > p.deadline) {
            p.isCancelled = true;
            p.location = Location.Cancelled;
            emit PackageCancelled(_id, "Deadline missed. Auto-cancelled.", block.timestamp);
        } else {
            revert("Deadline not missed yet");
        }
    }

    function viewTransactionHistory(uint _id) public view returns (TransferRecord[] memory) {
        return packageTransfers[_id];
    }

    // Function to check current status of order
    function viewCurrentStatus(uint _id) public view returns (
        address holder,
        Location location,
        uint deadline,
        bool onTime,
        bool cancelled
    ) {
        Package memory p = packages[_id];
        return (
            p.currentHolder,
            p.location,
            p.deadline,
            block.timestamp <= p.deadline,
            p.isCancelled
        );
    }

    function checkDeadline(uint _id) public view returns (bool) {
        return block.timestamp <= packages[_id].deadline;
    }
}
