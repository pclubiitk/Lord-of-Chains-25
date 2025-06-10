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

    modifier onlyRole(Role role) 
    {
        require(role==Role.Seller,"Not seller");
        _;
    }

    function mintProductNFT(string memory tokenURI,uint256 deliveryDeadline,Role role)
    public onlyRole(role) returns (uint256)
    {
        uint256 tokenId = _nextTokenId++;
        _mint(msg.sender, tokenId);
        _setTokenURI(tokenId, tokenURI);

        products[tokenId]=Product({
            tokenId:tokenId,
            currentRole: Role.Seller,
            createdAt: block.timestamp,
            deliveryDeadline: deliveryDeadline
        });
        return tokenId;

    }

    // The following functions are overrides required by Solidity.

    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage)
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

    enum Role{Seller,Warehouse,Delivery,Buyer}

    function getRoleName(Role role) internal pure returns (string memory)
    {
        if(role == Role.Seller){return "Seller";}
        else if(role == Role.Warehouse){return "Warehouse";}
        else if(role == Role.Delivery){return "Delivery";}
        else if(role == Role.Buyer){return "Buyer";}
        return "Unknown";
    }

    struct Product{
        uint256 tokenId;
        Role currentRole;
        uint256 createdAt;
        uint256 deliveryDeadline;
    }

    mapping(uint256=>Product) public products;

    struct TransferLog{
        string fromRole;
        string toRole;
        uint256 timestamp;
    }

    mapping (uint256 => TransferLog[]) public transferLogs;

    event TransferRole(uint256 tokenId, Role currentRole,uint256 timestamp);

    modifier validToken(uint256 tokenId) {
        require(_ownerOf(tokenId) != address(0), "Token does not exist");
        _;
    }

    function transferToNextRole(uint256 tokenId) public 
    {
        Product storage product = products[tokenId];
        Role role=product.currentRole;
        if(role ==Role.Seller)
            product.currentRole=Role.Warehouse;
        else if(role ==Role.Warehouse)
            product.currentRole=Role.Delivery;
        else if(role ==Role.Delivery)
            product.currentRole=Role.Buyer;
        else 
            revert("Product already delivered to buyer.")   ;

        //Log the event
        transferLogs[tokenId].push(
            TransferLog({
                fromRole:getRoleName(role),
                toRole:getRoleName(product.currentRole),
                timestamp :block.timestamp
            })
        );

        emit TransferRole(tokenId,product.currentRole,block.timestamp);
    }

    function getTransferHistory(uint256 tokenId) 
    public view validToken(tokenId)
    returns (TransferLog[] memory) 
    {
        return transferLogs[tokenId];
    }

    function getProducts() public view returns (Product[] memory)
    {
        Product[] memory _products=new Product[](_nextTokenId);
        for(uint i=0;i < _nextTokenId;i++)
        {
            _products[i]=products[i];
        }
        return _products;
    }
}