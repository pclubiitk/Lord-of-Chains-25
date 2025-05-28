# Bakchod Blockchain

Welcome to **Bakchod Blockchain**, a basic blockchain simulation in Python. This project demonstrates the fundamentals of blockchain technology, including:

- RSA digital signatures
- Block and transaction handling
- Mining simulation (Proof of Work style)
- Avalanche consensus algorithm (for probabilistic consensus)
- Node and miner simulation
- Simple CLI-based interaction

---

## 📁 Project Structure

The codebase has two main versions of the simulation:

1. **Mining-based Blockchain** – A traditional simulation with miners competing to mine blocks.
2. **Avalanche Consensus Blockchain** – A modern, probabilistic consensus mechanism simulating multiple rounds of voting.

### Supporting Modules

These classes are assumed to be defined in separate files:

- `Block` (in `block.py`) – Represents a block in the blockchain.
- `Node` (in `node.py`) – Represents a user or entity with a wallet and a blockchain.
- `Miner` (in `miner.py`) – Represents an entity that mines blocks and earns rewards.

---

## 🔐 Cryptography Used

- **RSA Digital Signature**
  - Messages (transactions) are hashed using SHA-256.
  - Signatures are generated using the sender’s private key.
  - Signature verification is done using the sender’s public key.

---

## 🚀 Features

### ✅ General

- User-friendly terminal interface.
- Transaction entry with real-time signature and verification.
- Node and miner balance management.
- Blockchain is stored locally per node (simulated decentralized behavior).

### ⚒️ Version 1: Mining-Based Blockchain

- Each block contains up to 3 transactions.
- Random miners "mine" the block and earn rewards.
- Nodes’ blockchain copies are updated after each block is mined.

### 🧠 Version 2: Avalanche Consensus Blockchain

- Each transaction is verified using a probabilistic voting model.
- Quorum-based voting with a configurable majority and threshold.
- Transactions are added only if they pass consensus.

---

## 🧪 How to Run

1. Make sure you have Python 3 installed.
2. Create the following Python files with your logic:
   - `block.py`
   - `node.py`
   - `miner.py` *(only needed for Mining version)*
3. Run either script:
   - For mining simulation:
     ```bash
     python mining_blockchain.py
     ```
   - For Avalanche consensus simulation:
     ```bash
     python avalanche_blockchain.py
     ```

---

## ⚙️ Configuration

- RSA Keys: User inputs two prime numbers `p` and `q` to generate keys.
- Avalanche Consensus:
  - `quorum = 20`
  - `majority = 70%`
  - `threshold = 5` consistent votes to finalize a decision.

---

## 📌 Sample Output

