// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract SupplyChainRegistry is ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _orderCounter;

    enum Stage { Created, AtWarehouse, InTransit, Completed }

    struct Order {
        Stage stage;
        uint256 packedAt;
        uint256 expiresAt;
        uint256 deliverBy;
        bool needsCooling;
        uint8 warehouseChecks;
        uint8 transportChecks;
    }

    struct LogEntry {
        Stage from;
        Stage to;
        uint256 time;
        string comment;
    }

    mapping(uint256 => Order) public orders;
    mapping(uint256 => LogEntry[]) public logs;
    mapping(address => Stage) public identities;

    event OrderMinted(uint256 indexed orderId, address indexed owner);
    event StageChanged(uint256 indexed orderId, Stage from, Stage to, string comment);
    event DeliveryOutcome(uint256 indexed orderId, bool onTime);

    constructor(address initialOwner) ERC721("SupplyOrder", "SPORD") Ownable(initialOwner) {
        // Owner initialized
    }

    modifier onlyStage(uint256 orderId, Stage required) {
        require(orders[orderId].stage == required, "Invalid stage");
        _;
    }

    function assignRole(Stage role) external {
        identities[msg.sender] = role;
    }

    function createOrder(
        string calldata metadataURI,
        uint256 shelfLife,
        uint256 eta,
        bool cold
    ) external onlyOwner returns (uint256) {
        _orderCounter.increment();
        uint256 orderId = _orderCounter.current();
        _safeMint(msg.sender, orderId);
        _setTokenURI(orderId, metadataURI);

        orders[orderId] = Order({
            stage: Stage.Created,
            packedAt: block.timestamp,
            expiresAt: block.timestamp + shelfLife,
            deliverBy: eta,
            needsCooling: cold,
            warehouseChecks: 0,
            transportChecks: 0
        });
        emit OrderMinted(orderId, msg.sender);
        return orderId;
    }

    function moveToWarehouse(uint256 orderId, string calldata note)
        external onlyStage(orderId, Stage.Created)
    {
        require(identities[msg.sender] == Stage.Created, "Not Seller");
        _recordTransition(orderId, Stage.AtWarehouse, note);
    }

    function confirmStorage(uint256 orderId)
        external onlyStage(orderId, Stage.AtWarehouse)
    {
        require(orders[orderId].needsCooling, "No cooling needed");
        orders[orderId].warehouseChecks++;
    }

    function shipOrder(uint256 orderId, string calldata note)
        external onlyStage(orderId, Stage.AtWarehouse)
    {
        require(identities[msg.sender] == Stage.AtWarehouse, "Not Warehouse");
        if (orders[orderId].needsCooling) {
            require(orders[orderId].warehouseChecks > 0, "Cooling not confirmed");
        }
        require(block.timestamp <= orders[orderId].expiresAt, "Order expired");
        _recordTransition(orderId, Stage.InTransit, note);
    }

    function deliverOrder(uint256 orderId, string calldata note)
        external onlyStage(orderId, Stage.InTransit)
    {
        require(identities[msg.sender] == Stage.InTransit, "Not Carrier");
        orders[orderId].transportChecks++;
        _recordTransition(orderId, Stage.Completed, note);

        bool onTime = block.timestamp <= orders[orderId].deliverBy;
        emit DeliveryOutcome(orderId, onTime);
    }

    function _recordTransition(
        uint256 orderId,
        Stage next,
        string memory comment
    ) private {
        Stage prev = orders[orderId].stage;
        orders[orderId].stage = next;
        logs[orderId].push(LogEntry(prev, next, block.timestamp, comment));
        emit StageChanged(orderId, prev, next, comment);
    }

    function getLogs(uint256 orderId) external view returns (LogEntry[] memory) {
        return logs[orderId];
    }
}