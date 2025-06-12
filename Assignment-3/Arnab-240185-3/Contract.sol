// SPDX-License-Identifier: MIT
// Compatible with OpenZeppelin Contracts ^5.0.0
pragma solidity ^0.8.27;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {ERC721URIStorage} from "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract SupplyChainNFT is ERC721, ERC721URIStorage, Ownable {
    uint256 private _nextTokenId;

    constructor(address initialOwner)
        ERC721("SupplyChainNFT", "SCNFT")
        Ownable(initialOwner)
    {}

    // Enum to define different roles in the supply chain
    enum Role { Seller, Warehouse, Delivery, Buyer }

    // Product struct to store essential product information
    struct Product {
        uint256 tokenId;
        Role currentRole;
        uint256 createdAt;
        uint256 deliveryDeadline;
        uint256 expiryDate;
        bool isTemperatureSensitive;
        bool coldStorageConfirmed;
    }

    // Enhanced TransferLog struct with audit note
    struct TransferLog {
        string fromRole;
        string toRole;
        uint256 timestamp;
        string auditNote;
    }

    // Mappings to store product data and transfer history
    mapping(uint256 => Product) public products;
    mapping(uint256 => TransferLog[]) public transferLogs;

    // Events for various supply chain activities
    event TransferRole(uint256 indexed tokenId, Role currentRole, uint256 timestamp);
    event ProductExpired(uint256 indexed tokenId, uint256 currentTimestamp);
    event DeliveryStatus(uint256 indexed tokenId, string status, uint256 timestamp);
    event ColdStorageConfirmed(uint256 indexed tokenId, uint256 timestamp);
    event ProductMinted(uint256 indexed tokenId, uint256 deliveryDeadline, uint256 expiryDate, bool isTemperatureSensitive);

    // Simple role check for minting - anyone can mint as seller
    modifier onlyRole(Role role) {
        require(role == Role.Seller, "Only seller role can mint");
        _;
    }

    // Modifier to validate token existence
    modifier validToken(uint256 tokenId) {
        require(_ownerOf(tokenId) != address(0), "Token does not exist");
        _;
    }

    /**
     * @dev Mint a new product NFT with comprehensive metadata
     * Following the assignment format for minting
     */
    function mintProductNFT(
        string memory tknURI, 
        uint256 deliveryDeadline,
        uint256 expiryDate,
        bool isTemperatureSensitive,
        Role role
    ) public onlyRole(role) returns (uint256) {
        // Basic validation checks
        require(deliveryDeadline > 0, "Delivery deadline must be in the future");
        require(expiryDate > 0, "Expiry date must be in the future");

        uint256 newTokenId = _nextTokenId;
        _mint(msg.sender, newTokenId);
        _setTokenURI(newTokenId, tknURI);

        // Store product information
        products[newTokenId] = Product({
            tokenId: newTokenId,
            currentRole: Role.Seller,
            createdAt: block.timestamp,
            deliveryDeadline: deliveryDeadline+block.timestamp,
            expiryDate: expiryDate+block.timestamp,
            isTemperatureSensitive: isTemperatureSensitive,
            coldStorageConfirmed: false
        });

        _nextTokenId++;
        emit ProductMinted(newTokenId, deliveryDeadline, expiryDate, isTemperatureSensitive);
        return newTokenId;
    }

    /**
     * @dev Confirm cold storage for temperature sensitive products
     * Must be called when product is in warehouse before transfer
     * Implements Temperature Sensitivity Rule
     */
    function confirmColdStorage(uint256 tokenId) public validToken(tokenId) {
        Product storage product = products[tokenId];
        require(product.currentRole == Role.Warehouse, "Product must be in warehouse");
        require(product.isTemperatureSensitive, "Product is not temperature sensitive");
        require(!product.coldStorageConfirmed, "Cold storage already confirmed");

        product.coldStorageConfirmed = true;
        emit ColdStorageConfirmed(tokenId, block.timestamp);
    }

    /**
     * @dev Transfer product to next role with audit note
     * Following the assignment's simple approach - anyone can call this
     * Implements the required 3 rules:
     * 1. Temperature Sensitivity Rule
     * 2. Expiry Date Rule  
     * 3. Audit Log Rule
     */
    function transferToNextRole(uint256 tokenId, string memory auditNote) public validToken(tokenId) {
        Product storage product = products[tokenId];
        
        // Rule 3: Audit Log Rule - audit note cannot be empty
        require(bytes(auditNote).length > 0, "Audit note cannot be empty");
        
        // Rule 2: Expiry Date Rule - check if product has expired
        if (block.timestamp > product.expiryDate) {
            emit ProductExpired(tokenId, block.timestamp);
            revert("Product has expired");
        }
        
        // Rule 1: Temperature Sensitivity Rule - check cold storage for warehouse transfers
        if (product.isTemperatureSensitive && product.currentRole == Role.Warehouse) {
            require(product.coldStorageConfirmed, "Cold storage must be confirmed before transfer");
        }

        Role previousRole = product.currentRole;
        
        // Role progression logic as per assignment
        if (product.currentRole == Role.Seller) {
            product.currentRole = Role.Warehouse;
        } else if (product.currentRole == Role.Warehouse) {
            product.currentRole = Role.Delivery;
        } else if (product.currentRole == Role.Delivery) {
            product.currentRole = Role.Buyer;
            // Check delivery status when reaching buyer
            checkDeliveryStatus(tokenId);
        } else {
            revert("Product already delivered to buyer");
        }

        // Log the transfer with audit note
        transferLogs[tokenId].push(
            TransferLog({
                fromRole: getRoleName(previousRole),
                toRole: getRoleName(product.currentRole),
                timestamp: block.timestamp,
                auditNote: auditNote
            })
        );

        emit TransferRole(tokenId, product.currentRole, block.timestamp);
    }

    /**
     * @dev Check delivery status when product reaches buyer
     * Internal function for delivery time auditing
     */
    function checkDeliveryStatus(uint256 tokenId) internal {
        Product storage product = products[tokenId];
        
        if (block.timestamp <= product.deliveryDeadline) {
            emit DeliveryStatus(tokenId, "OnTime", block.timestamp);
        } else {
            emit DeliveryStatus(tokenId, "Delayed", block.timestamp);
        }
    }

    /**
     * @dev Helper function to get role name as string
     * Following the assignment's format exactly
     */
    function getRoleName(Role role) internal pure returns (string memory) {
        if (role == Role.Seller) return "Seller";
        if (role == Role.Warehouse) return "Warehouse";
        if (role == Role.Delivery) return "Delivery";
        if (role == Role.Buyer) return "Buyer";
        return "Unknown";
    }

    /**
     * @dev Get complete transfer history for a product
     * Returns all transfer logs with audit notes
     */
    function getTransferHistory(uint256 tokenId) 
        public 
        view 
        validToken(tokenId)
        returns (TransferLog[] memory) 
    {
        return transferLogs[tokenId];
    }

    /**
     * @dev Get all products for debugging
     * Useful for testing the contract
     */
    function getProducts() public view returns (Product[] memory) {
        Product[] memory _products = new Product[](_nextTokenId);
        for (uint i = 0; i < _nextTokenId; i++) {
            _products[i] = products[i];
        }
        return _products;
    }

    /**
     * @dev Get detailed product information
     */
    function getProductDetails(uint256 tokenId) 
        public 
        view 
        validToken(tokenId) 
        returns (Product memory) 
    {
        return products[tokenId];
    }

    /**
     * @dev Get current role of a product
     */
    function getCurrentRole(uint256 tokenId) 
        public 
        view 
        validToken(tokenId) 
        returns (Role) 
    {
        return products[tokenId].currentRole;
    }

    // Required overrides for ERC721URIStorage
    function tokenURI(uint256 tokenId) 
        public 
        view 
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}