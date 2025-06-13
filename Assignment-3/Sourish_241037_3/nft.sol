// SPDX-License-Identifier: MIT
// Compatible with OpenZeppelin Contracts ^5.0.0

pragma solidity ^0.8.0;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {ERC721URIStorage} from "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract SupplyNFT is ERC721, ERC721URIStorage, Ownable {

    using Counters for Counters.Counter;

    Counters.Counter private _tokenIds;

    uint256 private _nextTokenId;

    constructor(address initialOwner)
        ERC721("MyToken", "MTK")
        Ownable(initialOwner)
    {}

    function safeMint(address to, string memory uri)
        public
        onlyOwner
        returns (uint256)
    {
        uint256 tokenId = _nextTokenId++;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        return tokenId;
    }

    // The following functions are overrides required by Solidity.

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

    enum Role {
        Seller,
        Warehouse,
        Delivery,
        Buyer
    }

    // Defining complex structures
    struct Package {
        uint id;
        uint deliveryDeadline;
        Role currentRole;     
        uint createdAt;
        bool isTemperatureSensitive;
    }

    struct TransferRecord {
        string from;
        string to;
        uint timestamp;
    }

    uint sellerLimit = 0;
    uint warehouseLimit = 0;
    uint deliveryLimit = 0;

    // Defining mappings to store order packages mapped with their order IDs
    mapping(uint => Package) public packages;
    mapping(uint => TransferRecord[]) public packageTransfers;
    mapping(address => Role) public userRoles;

    // Defining events
    event PackageTransferred(uint id, string auditNote, Role prevRole, Role curRole, uint time);
    event DeliveryStatus(uint id, string status, uint time);

    // Defining modifier
    modifier onlyRole(Role requiredRole) {
    require(userRoles[msg.sender] == requiredRole, "Access denied: incorrect role");
    _;
    }


    // Function to create a package as NFT 

    function mintProductNFT(string memory _tokenURI, bool isCold) public onlyRole(Role.Seller) returns (uint256) {
        uint deadline = block.timestamp + 120;

        uint256 newTokenId = _tokenIds.current(); 
        _safeMint(msg.sender, newTokenId);
        _setTokenURI(newTokenId, _tokenURI);
        packages[newTokenId] = Package({ 
            id: newTokenId,
            deliveryDeadline: deadline,
            currentRole: Role.Seller, 
            createdAt: block.timestamp,
            isTemperatureSensitive: isCold
        }); 
            
        _tokenIds.increment(); 
        return newTokenId; 
    }

    // Function to transfer the role of the package 
    function transferToNextRole(uint _id, string memory auditNote) public {
        Package storage package = packages[_id];

        Role prevRole = package.currentRole;

        require(bytes(auditNote).length>0,"Audit note should not be empty");
        if(package.currentRole == Role.Seller) {
            if(sellerLimit < 5) {
                package.currentRole = Role.Warehouse;
                sellerLimit++;
            }
            else {
                revert("Seller limit reached");
            }
        }
        else if(package.currentRole == Role.Warehouse) {
            if(warehouseLimit < 5) {
                    if(package.isTemperatureSensitive) {
                    package.currentRole = Role.Delivery;
                    warehouseLimit++;
                }
                else {
                    revert("Only cold storage products can be delivered");
                }
            }
            else {
                revert("Warehouse limit reached");
            }
            
        }
        else if(package.currentRole == Role.Delivery) {
            if(deliveryLimit < 5) {
                    package.currentRole = Role.Buyer;
                    deliveryLimit++;
                    if(package.deliveryDeadline >= block.timestamp) {
                    emit DeliveryStatus(_id,"On Time",block.timestamp);
                    }
            else {
                emit DeliveryStatus(_id,"Delayed",block.timestamp);
            }
            }
            else {
                revert("Delivery limit reached");
            }
        }
        else {
            revert("Package delivered to buyer");
        }


        packageTransfers[_id].push(TransferRecord({
            from: getRoleName(prevRole),
            to: getRoleName(package.currentRole),
            timestamp: block.timestamp
        }));

        emit PackageTransferred(_id, auditNote, prevRole, package.currentRole, block.timestamp);    

    }

    function getRoleName(Role role) internal pure returns (string memory) { 
        if (role == Role.Seller) return "Seller"; 
        if (role == Role.Warehouse) return "Warehouse"; 
        if (role == Role.Delivery) return "Delivery"; 
        if (role == Role.Buyer) return "Buyer"; 
        return "Unknown";
    }

    function getRole(uint _id) public view returns (string memory) {
        Package storage package = packages[_id];
        Role role = package.currentRole;
        if (role == Role.Seller) return "Seller"; 
        if (role == Role.Warehouse) return "Warehouse"; 
        if (role == Role.Delivery) return "Delivery"; 
        if (role == Role.Buyer) return "Buyer"; 
        return "Unknown";

    }

    function checkDeadline(uint _id) public view returns (string memory) {
        Package storage package = packages[_id];
        if (block.timestamp < package.deliveryDeadline) return "On Time"; 
        else return "Late";
    }
}

