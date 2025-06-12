# Tokenizing Supply Chain Products using NFTs

## Overview
This project demonstrates how supply chain products can be tokenized as NFTs (Non-Fungible Tokens) on the Ethereum blockchain. Each product is represented as a unique NFT, enabling transparent tracking, provenance, and secure ownership transfer.

## Features
- Mint NFTs for supply chain products (e.g., medicines, medical devices)
- Store product metadata (name, image, description, etc.)
- Transfer product ownership securely on-chain
- View product details and history

## Smart Contract
- **Contract Name:** SupplyChainNFT
- **Deployed Address:** `0x8A444311d5601012FF2bB1ab27f841671752110E`
- **Language:** Solidity

## Files
- `Contract.sol` – Main smart contract for NFT logic
- `metadata1.json`, `metadata2.json`, `metadata3.json` – Example metadata for products
- Product images: `BP monitor.jpg`, `calpol-650mg.jpg`, `covaxinjpg.jpg`
- `README.md` – Project documentation

## How to Use
1. **Deploy the Contract:**  
   Deploy `Contract.sol` to an Ethereum-compatible network 
2. **Mint NFTs:**  
   Call the minting function to create NFTs for each product, linking to their metadata. Set Role field =0 for seller for the purpose of minting.
3. **Transfer Ownership:**  
   Use the transfer function to change product ownership as items move through the supply chain.
4. **View Product Details:**  
   Retrieve metadata and ownership information for each NFT.

## Example Metadata
Each product NFT points to a metadata JSON file, e.g.:
```json
{
    "description": "Sphygmomanometer used for measuring blood pressure, featuring automatic inflation and digital display.",
    "external_url": "https://github.com/pclubiitk/Lord-of-Chains-25",
    "image": "https://turquoise-voluntary-mosquito-398.mypinata.cloud/ipfs/bafkreigwcprnng2id5k2xbts4zth63u7ebndqe4r6x7u4g4ibkyj2pnmy4",
    "name": "Omron HEM-7120 Automatic Blood Pressure Monitor NFT",
    "attributes": [
      {
        "trait_type": "Product Type",
        "value": "Medical Device"
      },
      {
        "trait_type": "Manufacturer",
        "value": "Omron Healthcare"
      },
      {
        "trait_type": "Temperature Sensitive",
        "value": "No"
      }
    ]
}
```

## Use Cases
- Pharmaceutical supply chain tracking
- Anti-counterfeiting for medical products
- Transparent product provenance

## License
This project is for educational purposes.

