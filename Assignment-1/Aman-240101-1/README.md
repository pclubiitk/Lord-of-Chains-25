# Simple Blockchain Implementation in Python

This is a basic blockchain simulation built with Python. It includes features like transaction creation, digital signature simulation, block mining with Proof of Work (PoW), and balance tracking across addresses.

---

## Files

```
.
├── blockchain.py         # Main Python script
├── blockchain.json       # Blockchain data file (auto-generated)
└── README.md             # This file
```

---

## Requirements

- Python 3.7 or higher
- No external libraries needed (uses Python standard library only)

---

## How to Use

### 1. Open Your Terminal

Navigate to the project directory:

```bash
cd path/to/project-directory
```

### 2. Run the Program

Use Python to execute the blockchain script:

```bash
python blockchain.py
```

---

## How It Works

1. **User Inputs**:  
   You'll be prompted to enter your public/private key, recipient address, and transaction amount.

2. **Digital Signature**:  
   A mock signature is created using SHA-256 on the private key + transaction data.

3. **Transaction Pool**:  
   You can add multiple transactions before mining.

4. **Mining Competition**:  
   Two miners (`miner1_pub`, `miner2_pub`) attempt to mine blocks. Each mined block rewards the miner.

5. **Balance Display**:  
   At the end, balances of all participants are shown.

---

## Features

-  Transaction creation and signing
-  Proof-of-Work mining
-  Mining rewards
-  Persistent blockchain file (`blockchain.json`)
-  Genesis block auto-creation
-  Balance calculation per address

---

## Proof of Work (PoW)

Mining works by finding a nonce such that the SHA-256 hash of the block starts with a certain number of leading zeros (difficulty = 4).

---

## Digital Signature 

This simulates digital signatures using:

```
signature = SHA256(private_key + transaction_data)
```

---

## Output Example

```text
Enter your public key: abc@123
Enter your private key (for signing): def@123
Enter recipient's public key: ghi@123
Enter amount: 50
Digital signature of transaction: <hash>

Add more transactions? (y/n): n

Miner miner1_pub starting mining competition...
Block 1 mined with hash: 0000ac45...

Miner miner2_pub starting mining competition...
Block 2 mined with hash: 00001ef2...

Balances:
Balance of abc@123: -50.0
Balance of ghi@123: 50.0
Balance of miner1_pub: 50.0
Balance of miner2_pub: 50.0
```

---

