// SPDX-License-Identifier: MIT
pragma solidity ^0.8.27;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

contract ProductOrderNFT is ERC721URIStorage, AccessControl {
    bytes32 public constant SELLER_ROLE = keccak256("SELLER_ROLE");
    bytes32 public constant WAREHOUSE_ROLE = keccak256("WAREHOUSE_ROLE");
    bytes32 public constant DELIVERY_ROLE = keccak256("DELIVERY_ROLE");
    bytes32 public constant BUYER_ROLE = keccak256("BUYER_ROLE");

    enum Status { Created, InWarehouse, InDelivery, Delivered }

    struct ProductInfo {
        bool isTemperatureSensitive;
        bool coldStorageConfirmed;
        uint256 expiryTimestamp;
        uint256 deliveryDeadline;
        Status status;
    }

    uint256[] public allTokenIds;
    mapping(uint256 => ProductInfo) public productInfo;
    mapping(uint256 => address) public orderBy;

    event ProductTransfer(
        uint256 indexed tokenId,
        string fromRole,
        string toRole,
        uint256 timestamp
    );
    event ProductExpired(uint256 indexed tokenId, uint256 timestamp);
    event DeliveryStatus(uint256 indexed tokenId, string status, uint256 timestamp);

    constructor(address seller, address warehouse, address delivery, address buyer)
        ERC721("ProductNFT", "PNFT")
    {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(SELLER_ROLE, seller);
        _grantRole(WAREHOUSE_ROLE, warehouse);
        _grantRole(DELIVERY_ROLE, delivery);
        _grantRole(BUYER_ROLE, buyer);
    }

    // Mint new product
    function safeMint(
        address to,
        uint256 tokenId,
        string memory uri,
        bool isTemperatureSensitive,
        uint256 expiryTimestamp,
        uint256 deliveryDeadline
    ) public onlyRole(SELLER_ROLE) {
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        productInfo[tokenId] = ProductInfo(
            isTemperatureSensitive,
            false,
            expiryTimestamp,
            deliveryDeadline,
            Status.Created
        );
        allTokenIds.push(tokenId);
    }

    // Seller transfers to Warehouse
    function transferToWarehouse(uint256 tokenId, address warehouse) public onlyRole(SELLER_ROLE) {
        require(productInfo[tokenId].status == Status.Created, "Not at Seller");
        _checkExpiry(tokenId);
        _transfer(ownerOf(tokenId), warehouse, tokenId);
        productInfo[tokenId].status = Status.InWarehouse;
        emit ProductTransfer(tokenId, "Seller", "Warehouse", block.timestamp);
    }

    // Warehouse confirms cold storage (if needed)
    function confirmColdStorage(uint256 tokenId) public onlyRole(WAREHOUSE_ROLE) {
        require(productInfo[tokenId].status == Status.InWarehouse, "Not in Warehouse");
        require(productInfo[tokenId].isTemperatureSensitive, "Not temp sensitive");
        productInfo[tokenId].coldStorageConfirmed = true;
    }

    // Warehouse transfers to Delivery
    function transferToDelivery(uint256 tokenId, address delivery) public onlyRole(WAREHOUSE_ROLE) {
        require(productInfo[tokenId].status == Status.InWarehouse, "Not in Warehouse");
        _checkExpiry(tokenId);
        if (productInfo[tokenId].isTemperatureSensitive) {
            require(productInfo[tokenId].coldStorageConfirmed, "Cold storage not confirmed");
        }
        _transfer(ownerOf(tokenId), delivery, tokenId);
        productInfo[tokenId].status = Status.InDelivery;
        // Reset cold storage confirmation for next cycle
        productInfo[tokenId].coldStorageConfirmed = false;
        emit ProductTransfer(tokenId, "Warehouse", "Delivery", block.timestamp);
    }

    // Delivery transfers to Buyer
    function transferToBuyer(uint256 tokenId, address buyer) public onlyRole(DELIVERY_ROLE) {
        require(productInfo[tokenId].status == Status.InDelivery, "Not in Delivery");
        _checkExpiry(tokenId);
        _transfer(ownerOf(tokenId), buyer, tokenId);
        productInfo[tokenId].status = Status.Delivered;
        emit ProductTransfer(tokenId, "Delivery", "Buyer", block.timestamp);

        // Delivery time auditing
        if (block.timestamp <= productInfo[tokenId].deliveryDeadline) {
            emit DeliveryStatus(tokenId, "OnTime", block.timestamp);
        } else {
            emit DeliveryStatus(tokenId, "Delayed", block.timestamp);
        }
    }

    // Internal expiry check
    function _checkExpiry(uint256 tokenId) internal {
        if (block.timestamp > productInfo[tokenId].expiryTimestamp) {
            emit ProductExpired(tokenId, block.timestamp);
            revert("Product expired");
        }
    }

    // Required overrides
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721URIStorage, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }
}
