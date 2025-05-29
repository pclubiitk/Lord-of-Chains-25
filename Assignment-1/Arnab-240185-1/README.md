# Blockchain Consensus Mechanisms Simulation

## What This Project Does
This project implements two major blockchain consensus mechanisms as educational simulations. It demonstrates the core concepts of cryptocurrency including digital signatures, consensus protocols, and distributed networks. The project includes both Bitcoin-style Proof of Work and the revolutionary Avalanche consensus mechanism.

## Two Complete Implementations

### 1. Bitcoin-Style Proof of Work (`bitcoin.py`)
Simulates how Bitcoin's blockchain works with mining competition and cryptographic proof of work.

### 2. Avalanche Consensus (`avalanche.py`) 
Implements the 4-phase Avalanche consensus protocol with 10 nodes using probabilistic sampling instead of mining.

## Key Features

### Bitcoin PoW Implementation
- **Proof of Work Mining**: Miners compete to solve cryptographic puzzles to earn block creation rights
- **Digital Signatures**: RSA-style cryptography secures transactions with unforgeable signatures  
- **Network Consensus**: All nodes maintain synchronized copies of the blockchain
- **Transaction Verification**: Cryptographic verification prevents unauthorized transactions
- **Balance Tracking**: UTXO-style balance calculation from complete transaction history
- **Mining Competition**: Multiple miners racing to find valid blocks with rewards
- **Transaction Mempool**: Pending transaction pool managed before mining

### Avalanche Consensus Implementation  
- **4-Phase Protocol**: Implements Slush -> Snowflake -> Snowball -> Avalanche phases
- **Probabilistic Sampling**: Nodes query random subsets for consensus decisions
- **10-Node Network**: Fixed network of 10 nodes demonstrating scalable consensus
- **Fast Finality**: Achieves consensus through repeated sampling without mining
- **Byzantine Fault Tolerance**: Robust against malicious or faulty nodes
- **Network Efficiency**: Lower energy consumption compared to Proof of Work

### Shared Features
- **Professional Implementation**: Clean, educational code suitable for academic submission
- **Data Persistence**: Complete blockchain state saved and reloadable between sessions
- **Modular Design**: Separate utilities for simulation and analysis
- **Educational Focus**: Heavily commented code explaining blockchain concepts

## How the Simulations Work

### Bitcoin PoW Simulation (`bitcoin.py`)
The program creates a small blockchain network with 5 participants:
- **You (The User)**: A regular participant who can send transactions
- **Two Miners**: Specialized nodes that compete to mine new blocks and earn rewards  
- **Two Other Nodes**: Additional network participants to receive transactions

Each participant starts with 50 coins distributed in the genesis block. You can create transactions to send coins to other participants. These transactions are digitally signed, verified, and then competed for by miners who try to include them in new blocks.

### Avalanche Consensus Simulation (`avalanche.py`)
The program creates a network with 10 nodes that use probabilistic consensus:
- **10 Equal Nodes**: All nodes participate equally in the consensus process
- **No Mining**: Consensus achieved through voting rather than computational work
- **4-Phase Process**: Each block goes through Slush, Snowflake, Snowball, and Avalanche phases
- **Random Sampling**: Nodes query random subsets of other nodes for opinions
- **Fast Finality**: Consensus reached quickly without energy-intensive mining

Each node starts with 100 coins. The simulation creates demo transactions and shows how the network reaches consensus on block acceptance through the multi-phase Avalanche protocol.

## Educational Value

These simulations help you understand:

### Bitcoin PoW Concepts
- How cryptocurrency transactions actually work under the hood
- Why mining is necessary and how it secures the network
- How digital signatures prevent fraud and unauthorized spending
- Why blockchain is considered tamper-resistant and secure
- How network consensus is achieved without a central authority

### Avalanche Consensus Concepts  
- How probabilistic consensus can replace energy-intensive mining
- The role of random sampling in achieving network agreement
- How multi-phase protocols increase consensus confidence
- Byzantine fault tolerance in distributed systems
- Scalability advantages of non-mining consensus mechanisms

### Comparative Analysis
- Trade-offs between Proof of Work and Avalanche consensus
- Energy efficiency differences between the mechanisms
- Security models and attack resistance
- Scalability and throughput characteristics
- Network finality and confirmation times

## Getting Started

### Requirements
- Python 3.7 or newer installed on your computer
- Basic understanding of how cryptocurrencies work (helpful but not required)
- About 10-15 minutes to run through each simulation

### Running the Bitcoin PoW Simulation

```bash
python bitcoin.py
```

This will start an interactive simulation where you can:
- Generate cryptographic keys for network participants
- Create and sign transactions
- Watch miners compete to add blocks to the blockchain
- See how consensus is maintained across the network

### Running the Avalanche Consensus Simulation

```bash
python avalanche.py
```

This will automatically run a demonstration showing:
- 10 nodes participating in Avalanche consensus
- The 4-phase consensus process in action
- How nodes reach agreement without mining
- Network state before and after consensus rounds

### Data Storage

Both simulations save their blockchain data:
- **Bitcoin PoW**: Saves to `blockchain_data/` directory
- **Avalanche**: Saves to `avalanche_data/` directory

You can examine the saved JSON files to see the complete blockchain state, transaction history, and node information.

### Running the Simulation
1. Ensure you have Python 3.7 or newer installed
2. Navigate to the Assignment-1 directory
3. Run the main simulation: `python main.py`
4. Follow the interactive prompts to create transactions and watch mining
5. View network statistics: `python view_balances.py`

### Additional Tools
- **`view_balances.py`**: Professional balance viewer for Bitcoin PoW simulation
- **`blockchain_data/`**: Bitcoin PoW persistent data storage
- **`avalanche_data/`**: Avalanche consensus persistent data storage

## Project Structure

```
Assignment-1/Arnab-240185-1/
├── bitcoin.py              # Bitcoin PoW blockchain simulation
├── avalanche.py            # Avalanche consensus simulation  
├── view_balances.py        # Bitcoin PoW balance viewer
├── question.txt            # Assignment requirements
├── README.md              # This documentation
├── blockchain_data/       # Bitcoin PoW saved data
│   ├── network_summary.json
│   ├── mempool.json
│   └── [Node directories]/
└── avalanche_data/        # Avalanche consensus saved data
    ├── network_summary.json
    └── [Node directories]/
```

## Technical Implementation Details

### Shared Components
Both implementations use the same cryptographic foundations:
- **RSA-style Digital Signatures**: Unforgeable transaction authentication
- **SHA-256 Hashing**: Block integrity and transaction IDs
- **JSON Data Persistence**: Human-readable blockchain storage

### Bitcoin PoW Specific
- **Proof of Work Mining**: Computational puzzle solving for block creation
- **Nonce Discovery**: Finding hash values with required difficulty
- **Mining Rewards**: Incentivizing network security through block rewards
- **Competitive Mining**: Multiple miners racing for block creation rights

### Avalanche Consensus Specific  
- **Probabilistic Sampling**: Random node querying for consensus
- **Multi-Phase Protocol**: Slush -> Snowflake -> Snowball -> Avalanche
- **Byzantine Fault Tolerance**: Robust against malicious nodes
- **Fast Finality**: Quick consensus without computational work

## Consensus Mechanism Comparison

| Aspect | Bitcoin PoW | Avalanche |
|--------|-------------|-----------|
| **Energy Use** | High (mining) | Low (voting) |
| **Speed** | ~10 minutes | Seconds |
| **Scalability** | Limited | High |
| **Security Model** | Longest chain | Probabilistic finality |
| **Node Requirements** | Variable | 10 fixed nodes |
| **Finality** | Probabilistic | Deterministic |

## Educational Applications

These simulations are perfect for:
- **Blockchain Education**: Comparing different consensus mechanisms
- **Computer Science**: Understanding distributed systems and cryptography
- **Cryptocurrency Research**: Analyzing trade-offs between protocols
- **Academic Projects**: Demonstrating practical blockchain implementations
- **Protocol Design**: Learning how consensus mechanisms work

Both implementations are heavily commented to explain the underlying concepts, making them excellent learning resources for understanding blockchain technology from multiple perspectives.

## Assignment Objectives Fulfilled

### Objective 1: Bitcoin PoW Implementation [COMPLETED]
- [x] Multiple nodes with miners using OOP design
- [x] User key input and transaction creation
- [x] Digital signature display and verification  
- [x] Transaction verification and temporary storage
- [x] Mining competition with different transaction subsets
- [x] Block validation and blockchain immutability
- [x] Balance tracking and mining rewards
- [x] Complete file system persistence

### Objective 2: Avalanche Consensus Implementation [COMPLETED]
- [x] 10 randomized nodes implementing 4-phase Avalanche protocol
- [x] Slush, Snowflake, Snowball, Avalanche phases
- [x] Probabilistic consensus through repeated sampling
- [x] Blockchain structure (not DAG) as specified
- [x] Simple demo with automatic transaction processing
- [x] Network consensus without mining competition