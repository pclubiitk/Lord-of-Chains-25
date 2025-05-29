# Proof-of-Work Blockchain Implementation in Python

This project implements a blockchain with a Proof-of-Work (PoW) consensus mechanism, featuring competitive mining between nodes using Python's threading module.

## Key Features

- **Full Blockchain Implementation** with blocks, transactions, and mining
- **Competitive Mining System** where miners race to solve the cryptographic puzzle
- **Thread-Safe Operations** using Python's synchronization primitives
- **Cryptographic Security** with RSA signatures and SHA-256 hashing
- **Interactive CLI** for managing nodes and transactions

## Core Components

### 1. Blockchain Architecture

```python
class Blockchain:
    def __init__(self):
        self.blocks = []
        self.__difficulty = 4  # Number of leading zeros required
        self.lock = threading.Lock()  # For thread-safe operations
```

1. Maintains the chain of validated blocks

2. Implements difficulty adjustment for mining

3. Uses threading.Lock() for synchronization

### 2. Node System

```python
class Node:
    def __init__(self, name, block_chain):
        self.private_key = RSA.generate(2048)
        self.public_key = self.private_key.publickey()
        self.balance = 1000  # Starting balance
```

1. Each node has cryptographic identity (RSA keypair)

2. Maintains individual balance

3. Can initiate transactions

### 3. Miner Implementation

```python
class Miner(Node):
    def mine_block(self, block_template, difficulty, stop_event):
        while not stop_event.is_set():
            # Mining attempts here
            if hash_matches:
                with result_lock:
                    if not stop_event.is_set():
                        stop_event.set()  # Signal other miners to stop
```

1. Inherits from Node with additional mining capability

2. Competes to solve PoW puzzle

3. Uses threading.Event for mining coordination

## Mining Mechanism

### Competitive Mining Process

##### 1. Transaction Pooling:

- Transactions are collected in a pool

- Verified before being added to a block

##### 2. Block Creation:
```python
block_template = {
    'index': len(blockchain),
    'transactions': [...],
    'previous_hash': last_block_hash,
    'nonce': 0
}
```
this is a block template in the create_block function of blockchain
each miner takes a copy of it and modify it to prevent collision with
other miner trying to acces the same memory location

##### 3. Threaded Mining:
- Multiple miners work simultaneously

- Each in their own thread with local block copy

- First to find valid nonce wins

##### 4. Consensus Achievement:
- Winner broadcasts solution

- stop_event triggers other miners to halt

- Block added to chain


