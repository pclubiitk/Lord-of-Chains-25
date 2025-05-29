# Bitcoin PoW Blockchain Simulation
# A complete implementation of a blockchain with Proof of Work consensus mechanism

import hashlib
import json
import time
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import threading
import os

# Cryptographic utilities for key generation and digital signatures
class CryptographicUtils:
    """Utility class for cryptographic operations including key generation and signing"""
    
    @staticmethod
    def generate_keys_from_primes(p: int, q: int) -> Tuple[Tuple[int, int], int]:
        """
        Generate RSA-like public and private keys from two prime numbers
        Returns: ((public_key_n, public_key_e), private_key_d)
        """
        if p == q:
            raise ValueError("p and q must be different prime numbers")
        
        n = p * q
        phi = (p - 1) * (q - 1)
        
        # Use a common public exponent
        e = 65537
        
        # Calculate private exponent using extended Euclidean algorithm
        try:
            d = CryptographicUtils._mod_inverse(e, phi)
        except ValueError as ex:
            raise ValueError(f"Failed to generate keys with primes {p} and {q}: {ex}")
        
        return ((n, e), d)
    
    @staticmethod
    def _mod_inverse(a: int, m: int) -> int:
        """Calculate modular inverse using extended Euclidean algorithm"""
        if CryptographicUtils._gcd(a, m) != 1:
            raise ValueError(f"Modular inverse does not exist for {a} and {m} (GCD != 1)")
        
        # Extended Euclidean Algorithm
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        
        _, x, _ = extended_gcd(a, m)
        return (x % m + m) % m
    
    @staticmethod
    def _gcd(a: int, b: int) -> int:
        """Calculate Greatest Common Divisor"""
        while b:
            a, b = b, a % b
        return a
    
    @staticmethod
    def sign_message(message: str, private_key: int, n: int) -> int:
        """
        Create a digital signature for a message using private key
        Simplified RSA-like signing
        """
        message_hash = int(hashlib.sha256(message.encode()).hexdigest(), 16)
        # Use modular exponentiation to sign
        signature = pow(message_hash % n, private_key, n)
        return signature
    
    @staticmethod
    def verify_signature(message: str, signature: int, public_key: Tuple[int, int]) -> bool:
        """
        Verify a digital signature using public key
        Returns True if signature is valid
        """
        n, e = public_key
        message_hash = int(hashlib.sha256(message.encode()).hexdigest(), 16)
        
        # Verify signature using public key
        decrypted = pow(signature, e, n)
        return decrypted == (message_hash % n)

@dataclass
class Transaction:
    """
    Represents a single transaction in the blockchain
    Contains sender, recipient, amount, and digital signature
    """
    sender_public_key: Tuple[int, int]  # (n, e) for RSA-like keys
    recipient_public_key: Tuple[int, int]
    amount: float
    timestamp: float
    signature: Optional[int] = None
    transaction_id: Optional[str] = None
    
    def __post_init__(self):
        """Generate transaction ID after initialization"""
        if not self.transaction_id:
            self.transaction_id = self.calculate_transaction_id()
    
    def calculate_transaction_id(self) -> str:
        """Calculate unique transaction ID based on transaction data"""
        transaction_string = f"{self.sender_public_key}{self.recipient_public_key}{self.amount}{self.timestamp}"
        return hashlib.sha256(transaction_string.encode()).hexdigest()
    
    def to_string(self) -> str:
        """Convert transaction to string for signing/hashing"""
        return f"{self.sender_public_key[0]}_{self.sender_public_key[1]}_{self.recipient_public_key[0]}_{self.recipient_public_key[1]}_{self.amount}_{self.timestamp}"
    
    def sign_transaction(self, private_key: int):
        """Sign the transaction with the sender's private key"""
        message = self.to_string()
        self.signature = CryptographicUtils.sign_message(message, private_key, self.sender_public_key[0])
    
    def verify_transaction(self) -> bool:
        """Verify the transaction signature"""
        if not self.signature:
            return False
        message = self.to_string()
        return CryptographicUtils.verify_signature(message, self.signature, self.sender_public_key)
    
    def to_dict(self) -> Dict:
        """Convert transaction to dictionary for JSON serialization"""
        return asdict(self)

@dataclass
class Block:
    """
    Represents a block in the blockchain
    Contains transactions, previous block hash, and mining information
    """
    index: int
    timestamp: float
    transactions: List[Transaction]
    previous_hash: str
    nonce: int = 0
    hash: Optional[str] = None
    miner_public_key: Optional[Tuple[int, int]] = None
    
    def __post_init__(self):
        """Calculate block hash after initialization"""
        if not self.hash:
            self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """
        Calculate the hash of the block
        Used for mining and block verification
        """
        # Create a string representation of the block
        transactions_string = json.dumps([tx.to_dict() for tx in self.transactions], sort_keys=True)
        block_string = f"{self.index}{self.timestamp}{transactions_string}{self.previous_hash}{self.nonce}"
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int, miner_public_key: Tuple[int, int]) -> int:
        """
        Mine the block by finding a nonce that produces a hash with required difficulty
        Returns the nonce that was found
        """
        self.miner_public_key = miner_public_key
        target = "0" * difficulty
        
        print(f"Mining block {self.index}... Target: {target}")
        start_time = time.time()
        
        print("Welcome! Let's create your first transaction.")
        print("You can send coins to any of the other nodes in the network.")
        print("Each transaction will be digitally signed and verified before being added to the blockchain.")
        
        while True:
            self.hash = self.calculate_hash()
            if self.hash.startswith(target):
                end_time = time.time()
                print(f"Block {self.index} mined! Nonce: {self.nonce}, Hash: {self.hash}")
                print(f"Mining time: {end_time - start_time:.2f} seconds")
                return self.nonce
            self.nonce += 1
            
            # Prevent infinite loops in case of issues
            if self.nonce > 1000000:
                print("Mining taking too long, reducing difficulty...")
                break
        
        return self.nonce
    
    def is_valid(self, previous_block_hash: str, difficulty: int) -> bool:
        """
        Validate the block by checking:
        1. Hash integrity
        2. Previous block hash
        3. Proof of work (difficulty)
        4. Transaction signatures
        """
        # Check if calculated hash matches stored hash
        if self.hash != self.calculate_hash():
            return False
        
        # Check if previous hash matches
        if self.previous_hash != previous_block_hash:
            return False
        
        # Check proof of work
        if not self.hash.startswith("0" * difficulty):
            return False
        
        # Verify all transaction signatures
        for transaction in self.transactions:
            if not transaction.verify_transaction():
                return False
        
        return True

class Node:
    """
    Represents a node in the blockchain network
    Stores blockchain copy and handles balance tracking
    """
    
    def __init__(self, name: str, public_key: Tuple[int, int], private_key: int):
        self.name = name
        self.public_key = public_key
        self.private_key = private_key
        self.blockchain = []
        self.balance = 0.0
        self.is_miner = False
    
    def add_block(self, block: Block):
        """Add a validated block to the node's blockchain copy"""
        self.blockchain.append(block)
        self.update_balance()
    
    def update_balance(self):
        """
        Calculate current balance by processing all transactions in the blockchain
        This demonstrates UTXO-like balance calculation
        """
        self.balance = 0.0
        
        for block in self.blockchain:
            for transaction in block.transactions:
                # If this node received money
                if transaction.recipient_public_key == self.public_key:
                    self.balance += transaction.amount
                
                # If this node sent money
                if transaction.sender_public_key == self.public_key:
                    self.balance -= transaction.amount
    
    def get_balance(self) -> float:
        """Get current balance of the node"""
        self.update_balance()
        return self.balance
    
    def create_transaction(self, recipient_public_key: Tuple[int, int], amount: float) -> Optional[Transaction]:
        """
        Create and sign a new transaction
        Returns None if insufficient balance
        """
        if self.get_balance() < amount:
            print(f"Insufficient balance! Current balance: {self.balance}, Requested: {amount}")
            return None
        
        transaction = Transaction(
            sender_public_key=self.public_key,
            recipient_public_key=recipient_public_key,
            amount=amount,
            timestamp=time.time()
        )
        
        # Sign the transaction
        transaction.sign_transaction(self.private_key)
        
        return transaction

class Miner(Node):
    """
    Miner class extends Node with mining capabilities
    Can compete to mine blocks and earn rewards
    """
    
    def __init__(self, name: str, public_key: Tuple[int, int], private_key: int):
        super().__init__(name, public_key, private_key)
        self.is_miner = True
        self.mining_reward = 50.0
    
    def mine_block(self, transactions: List[Transaction], previous_block: Block, difficulty: int) -> Block:
        """
        Mine a new block with given transactions
        Includes mining reward transaction
        """
        # Add mining reward transaction
        reward_transaction = Transaction(
            sender_public_key=(0, 0),  # System sender
            recipient_public_key=self.public_key,
            amount=self.mining_reward,
            timestamp=time.time(),
            signature=0  # System transactions don't need signatures
        )
        
        # Combine reward with other transactions
        all_transactions = [reward_transaction] + transactions
        
        # Create new block
        new_block = Block(
            index=previous_block.index + 1 if previous_block else 0,
            timestamp=time.time(),
            transactions=all_transactions,
            previous_hash=previous_block.hash if previous_block else "0"
        )
        
        # Mine the block
        new_block.mine_block(difficulty, self.public_key)
        
        return new_block

class Blockchain:
    """
    Main blockchain class that manages the entire network
    Handles consensus, mining competition, and network state
    """
    
    def __init__(self, difficulty: int = 4):
        self.nodes: List[Node] = []
        self.miners: List[Miner] = []
        self.mempool: List[Transaction] = []  # Pending transactions
        self.difficulty = difficulty
        self.blockchain_dir = "blockchain_data"
        
        # Create blockchain directory if it doesn't exist
        if not os.path.exists(self.blockchain_dir):
            os.makedirs(self.blockchain_dir)
        
        # Load existing blockchain or create genesis block
        self.load_blockchain()
    
    def add_node(self, node: Node):
        """Add a new node to the network"""
        self.nodes.append(node)
        if isinstance(node, Miner):
            self.miners.append(node)
    
    def create_genesis_block(self):
        """
        Create the genesis block with initial coin distribution
        Awards 50 coins to each node in the network
        """
        print("\n=== Creating Genesis Block ===")
        genesis_transactions = []
        
        # Award 50 coins to each node from the system
        for node in self.nodes:
            genesis_transaction = Transaction(
                sender_public_key=(0, 0),  # System sender
                recipient_public_key=node.public_key,
                amount=50.0,
                timestamp=time.time(),
                signature=0  # System transactions don't need signatures
            )
            genesis_transactions.append(genesis_transaction)
            print(f"Awarded 50 coins to {node.name}")
        
        # Create genesis block
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=genesis_transactions,
            previous_hash="0"
        )
        
        # Mine genesis block
        if self.miners:
            genesis_block.mine_block(self.difficulty, self.miners[0].public_key)
        
        # Add genesis block to all nodes
        for node in self.nodes:
            node.add_block(genesis_block)
        
        print(f"Genesis block created with hash: {genesis_block.hash}")
        print("=== Genesis Block Created ===\n")
    
    def add_transaction_to_mempool(self, transaction: Transaction):
        """Add a verified transaction to the mempool"""
        if transaction.verify_transaction():
            self.mempool.append(transaction)
            print(f"Transaction added to mempool: {transaction.transaction_id[:8]}...")
            print(f"Digital Signature: {transaction.signature}")
        else:
            print("Invalid transaction signature! Transaction rejected.")
    
    def mine_next_block(self):
        """
        Simulate mining competition between miners
        Each miner takes different subsets of transactions
        """
        if not self.mempool:
            print("No transactions in mempool to mine.")
            return
        
        if not self.miners:
            print("No miners available.")
            return
        
        print(f"\n=== Mining Competition Started ===")
        print(f"Transactions in mempool: {len(self.mempool)}")
        
        # Get the latest block
        latest_block = self.nodes[0].blockchain[-1] if self.nodes[0].blockchain else None
        
        # Divide transactions between miners (2 transactions per block as requested)
        transactions_per_block = 2
        mining_results = []
        
        # Each miner gets different subsets of transactions
        for i, miner in enumerate(self.miners):
            start_idx = i * transactions_per_block
            end_idx = min(start_idx + transactions_per_block, len(self.mempool))
            
            if start_idx >= len(self.mempool):
                break
            
            miner_transactions = self.mempool[start_idx:end_idx]
            
            print(f"\nMiner {miner.name} competing for block with {len(miner_transactions)} transactions")
            
            # Start mining in separate thread to simulate competition
            def mine_worker(miner, transactions, latest_block):
                try:
                    start_time = time.time()
                    block = miner.mine_block(transactions, latest_block, self.difficulty)
                    end_time = time.time()
                    mining_results.append((miner, block, end_time - start_time))
                except Exception as e:
                    print(f"Mining error for {miner.name}: {e}")
            
            # For simulation, we'll mine sequentially but with randomized timing
            mine_worker(miner, miner_transactions, latest_block)
            
            # Add some randomness to simulate network delays
            time.sleep(random.uniform(0.1, 0.3))
        
        # Select the winning block (first valid block or random selection for demo)
        if mining_results:
            winner_miner, winning_block, mining_time = random.choice(mining_results)  # Simulate random winner
            
            print(f"\nMiner {winner_miner.name} won the mining competition!")
            print(f"Block hash: {winning_block.hash}")
            print(f"Mining time: {mining_time:.2f} seconds")
            
            # Add winning block to all nodes
            for node in self.nodes:
                node.add_block(winning_block)
            
            # Remove mined transactions from mempool
            mined_transaction_ids = [tx.transaction_id for tx in winning_block.transactions if tx.sender_public_key != (0, 0)]
            self.mempool = [tx for tx in self.mempool if tx.transaction_id not in mined_transaction_ids]
            
            print(f"Block added to blockchain. New blockchain length: {len(self.nodes[0].blockchain)}")
        
        print("=== Mining Competition Ended ===\n")
    
    def display_network_status(self):
        """Display current status of all nodes in the network"""
        print("\n=== Network Status ===")
        print(f"Blockchain length: {len(self.nodes[0].blockchain)}")
        print(f"Transactions in mempool: {len(self.mempool)}")
        print("\nNode Balances:")
        
        for node in self.nodes:
            node_type = "Miner" if node.is_miner else "Node"
            print(f"  {node.name} ({node_type}): {node.get_balance():.2f} coins")
        
        print("=== Network Status End ===\n")
    
    def save_blockchain(self):
        """Save blockchain state to subdirectories for each node in human-readable format"""
        try:
            print(f"\nSaving blockchain data to {self.blockchain_dir}/...")
            
            # Save data for each node
            for node in self.nodes:
                node_dir = os.path.join(self.blockchain_dir, node.name)
                
                # Create node directory if it doesn't exist
                if not os.path.exists(node_dir):
                    os.makedirs(node_dir)
                
                # Prepare blockchain data for this node
                blockchain_data = {
                    "node_name": node.name,
                    "node_type": "Miner" if node.is_miner else "Node",
                    "blockchain_length": len(node.blockchain),
                    "blocks": []
                }
                
                # Convert each block to dictionary format
                for i, block in enumerate(node.blockchain):
                    block_data = {
                        "block_index": block.index,
                        "timestamp": block.timestamp,
                        "previous_hash": block.previous_hash,
                        "hash": block.hash,
                        "nonce": block.nonce,
                        "miner_public_key": block.miner_public_key,
                        "transactions": []
                    }
                    
                    # Convert each transaction to dictionary format
                    for tx in block.transactions:
                        tx_data = {
                            "transaction_id": tx.transaction_id,
                            "sender_public_key": tx.sender_public_key,
                            "recipient_public_key": tx.recipient_public_key,
                            "amount": tx.amount,
                            "timestamp": tx.timestamp,
                            "signature": tx.signature
                        }
                        block_data["transactions"].append(tx_data)
                    
                    blockchain_data["blocks"].append(block_data)
                
                # Save blockchain data as JSON
                blockchain_file = os.path.join(node_dir, "blockchain.json")
                with open(blockchain_file, 'w') as f:
                    json.dump(blockchain_data, f, indent=2, sort_keys=True)
                
                # Save node information
                node_info = {
                    "node_name": node.name,
                    "node_type": "Miner" if node.is_miner else "Node",
                    "public_key": {
                        "n": node.public_key[0],
                        "e": node.public_key[1]
                    },
                    "current_balance": node.get_balance(),
                    "is_miner": node.is_miner,
                    "mining_reward": getattr(node, 'mining_reward', None) if hasattr(node, 'mining_reward') else None
                }
                
                node_info_file = os.path.join(node_dir, "node_info.json")
                with open(node_info_file, 'w') as f:
                    json.dump(node_info, f, indent=2, sort_keys=True)
                
                print(f"[SUCCESS] Saved data for {node.name} in {node_dir}/")
            
            # Save mempool data
            mempool_data = {
                "pending_transactions_count": len(self.mempool),
                "transactions": []
            }
            
            for tx in self.mempool:
                tx_data = {
                    "transaction_id": tx.transaction_id,
                    "sender_public_key": tx.sender_public_key,
                    "recipient_public_key": tx.recipient_public_key,
                    "amount": tx.amount,
                    "timestamp": tx.timestamp,
                    "signature": tx.signature
                }
                mempool_data["transactions"].append(tx_data)
            
            mempool_file = os.path.join(self.blockchain_dir, "mempool.json")
            with open(mempool_file, 'w') as f:
                json.dump(mempool_data, f, indent=2, sort_keys=True)
            
            # Save network summary
            network_summary = {
                "network_info": {
                    "total_nodes": len(self.nodes),
                    "total_miners": len(self.miners),
                    "blockchain_length": len(self.nodes[0].blockchain) if self.nodes else 0,
                    "difficulty": self.difficulty,
                    "pending_transactions": len(self.mempool)
                },
                "nodes": []
            }
            
            for node in self.nodes:
                node_summary = {
                    "name": node.name,
                    "type": "Miner" if node.is_miner else "Node",
                    "public_key": node.public_key,
                    "balance": node.get_balance()
                }
                network_summary["nodes"].append(node_summary)
            
            summary_file = os.path.join(self.blockchain_dir, "network_summary.json")
            with open(summary_file, 'w') as f:
                json.dump(network_summary, f, indent=2, sort_keys=True)
            
            print(f"[SUCCESS] Saved mempool data")
            print(f"[SUCCESS] Saved network summary")
            print(f"\nBlockchain data successfully saved to {self.blockchain_dir}/")
            print(f"Each node has its own subdirectory with blockchain.json and node_info.json")
            
        except Exception as e:
            print(f"Error saving blockchain: {e}")
    
    def load_blockchain(self):
        """Load blockchain state from JSON directory structure"""
        try:
            network_summary_file = os.path.join(self.blockchain_dir, "network_summary.json")
            mempool_file = os.path.join(self.blockchain_dir, "mempool.json")
            
            if os.path.exists(network_summary_file):
                print(f"Loading existing blockchain from {self.blockchain_dir}/...")
                
                # Load network summary
                with open(network_summary_file, 'r') as f:
                    network_summary = json.load(f)
                
                print(f"Found network with {network_summary['network_info']['total_nodes']} nodes")
                
                # Load each node
                for node_info in network_summary['nodes']:
                    node_name = node_info['name']
                    node_dir = os.path.join(self.blockchain_dir, node_name)
                    
                    if os.path.exists(node_dir):
                        # Load node information
                        node_info_file = os.path.join(node_dir, "node_info.json")
                        blockchain_file = os.path.join(node_dir, "blockchain.json")
                        
                        if os.path.exists(node_info_file) and os.path.exists(blockchain_file):
                            # Load node details
                            with open(node_info_file, 'r') as f:
                                node_data = json.load(f)
                            
                            # Reconstruct public key tuple
                            public_key = (node_data['public_key']['n'], node_data['public_key']['e'])
                            
                            # Create node object (we'll need to ask for private key again for security)
                            if node_data['is_miner']:
                                # For demo, we'll use a placeholder private key since we can't store it
                                node = Miner(node_name, public_key, 1)  # Placeholder private key
                                if 'mining_reward' in node_data and node_data['mining_reward'] is not None:
                                    node.mining_reward = node_data['mining_reward']
                            else:
                                node = Node(node_name, public_key, 1)  # Placeholder private key
                            
                            # Load blockchain data
                            with open(blockchain_file, 'r') as f:
                                blockchain_data = json.load(f)
                            
                            # Reconstruct blockchain for this node
                            for block_data in blockchain_data['blocks']:
                                # Reconstruct transactions
                                transactions = []
                                for tx_data in block_data['transactions']:
                                    # Reconstruct public key tuples
                                    sender_key = tuple(tx_data['sender_public_key']) if tx_data['sender_public_key'] != [0, 0] else (0, 0)
                                    recipient_key = tuple(tx_data['recipient_public_key'])
                                    
                                    transaction = Transaction(
                                        sender_public_key=sender_key,
                                        recipient_public_key=recipient_key,
                                        amount=tx_data['amount'],
                                        timestamp=tx_data['timestamp'],
                                        signature=tx_data['signature'],
                                        transaction_id=tx_data['transaction_id']
                                    )
                                    transactions.append(transaction)
                                
                                # Reconstruct block
                                block = Block(
                                    index=block_data['block_index'],
                                    timestamp=block_data['timestamp'],
                                    transactions=transactions,
                                    previous_hash=block_data['previous_hash'],
                                    nonce=block_data['nonce'],
                                    hash=block_data['hash']
                                )
                                
                                if block_data['miner_public_key']:
                                    block.miner_public_key = tuple(block_data['miner_public_key'])
                                
                                node.blockchain.append(block)
                            
                            # Add node to network
                            self.add_node(node)
                            print(f"[SUCCESS] Loaded {node_name} with {len(node.blockchain)} blocks")
                
                # Load mempool if it exists
                if os.path.exists(mempool_file):
                    with open(mempool_file, 'r') as f:
                        mempool_data = json.load(f)
                    
                    for tx_data in mempool_data['transactions']:
                        sender_key = tuple(tx_data['sender_public_key']) if tx_data['sender_public_key'] != [0, 0] else (0, 0)
                        recipient_key = tuple(tx_data['recipient_public_key'])
                        
                        transaction = Transaction(
                            sender_public_key=sender_key,
                            recipient_public_key=recipient_key,
                            amount=tx_data['amount'],
                            timestamp=tx_data['timestamp'],
                            signature=tx_data['signature'],
                            transaction_id=tx_data['transaction_id']
                        )
                        self.mempool.append(transaction)
                    
                    print(f"[SUCCESS] Loaded {len(self.mempool)} pending transactions from mempool")
                
                # Update difficulty if stored
                if 'difficulty' in network_summary['network_info']:
                    self.difficulty = network_summary['network_info']['difficulty']
                
                print(f"[SUCCESS] Blockchain successfully loaded from {self.blockchain_dir}/")
                print(f"  Network: {len(self.nodes)} nodes, {len(self.miners)} miners")
                print(f"  Blockchain length: {len(self.nodes[0].blockchain) if self.nodes else 0}")
                print(f"  Pending transactions: {len(self.mempool)}")
                
                return True
                
            else:
                print("No existing blockchain data found. Will create new blockchain.")
                return False
                
        except Exception as e:
            print(f"Error loading blockchain: {e}")
            print("Will create new blockchain.")
            return False

def get_user_input_for_keys(node_name: str):
    """Get prime numbers from user for key generation"""
    print(f"\n=== Key Generation for {node_name} ===")
    print(f"To generate cryptographic keys for {node_name}, we need two prime numbers.")
    print("Please enter two 5-digit prime numbers. These will be used to create the public and private keys.")
    print("Example prime numbers you could use: 10007, 10009, 10037, 10039, 10061, 10067")
    
    while True:
        try:
            p = int(input(f"Enter first 5-digit prime number for {node_name}: "))
            q = int(input(f"Enter second 5-digit prime number for {node_name}: "))
            
            if len(str(p)) != 5 or len(str(q)) != 5:
                print("Please enter exactly 5-digit numbers.")
                continue
            
            if p == q:
                print("Please enter two different prime numbers.")
                continue
            
            # Simple primality check (not cryptographically secure, for demo only)
            def is_prime_simple(n):
                if n < 2:
                    return False
                for i in range(2, int(n**0.5) + 1):
                    if n % i == 0:
                        return False
                return True
            
            if not is_prime_simple(p) or not is_prime_simple(q):
                print("Please enter prime numbers only.")
                continue
            
            print(f"Keys generated successfully for {node_name}!")
            return p, q
            
        except ValueError:
            print("Please enter valid integers.")

def main():
    """
    Main function to run the blockchain simulation
    Handles user interaction and demonstrates all features
    """
    print("Bitcoin PoW Blockchain Simulation Started")
    print("=" * 50)
    
    # Initialize blockchain with difficulty 3 (for faster demo)
    blockchain = Blockchain(difficulty=3)
    
    # Check if existing blockchain data exists
    existing_data_loaded = False
    if blockchain.nodes:
        print(f"\n=== Existing Blockchain Found ===")
        print(f"Found existing blockchain with {len(blockchain.nodes)} nodes:")
        for node in blockchain.nodes:
            node_type = "Miner" if node.is_miner else "Node"
            balance = node.get_balance()
            print(f"  - {node.name} ({node_type}): {balance:.2f} coins")
        print(f"Blockchain length: {len(blockchain.nodes[0].blockchain) if blockchain.nodes else 0}")
        print(f"Pending transactions: {len(blockchain.mempool)}")
        
        while True:
            choice = input("\nWould you like to (1) Continue with existing data or (2) Start fresh? Enter 1 or 2: ").strip()
            if choice == "1":
                existing_data_loaded = True
                print("Continuing with existing blockchain data...")
                
                # Note: For security, private keys aren't stored, so transactions can't be created
                # In a real system, users would need to import their private keys
                print("\nNote: Private keys are not stored for security. You can view the blockchain but cannot create new transactions.")
                print("To create transactions, please start fresh or implement proper key management.")
                break
            elif choice == "2":
                print("Starting fresh blockchain...")
                # Clear existing data
                blockchain.nodes = []
                blockchain.miners = []
                blockchain.mempool = []
                break
            else:
                print("Please enter 1 or 2.")
    
    # Create nodes if no existing data or user chose to start fresh
    if not existing_data_loaded:
        # Create 5 nodes (2 miners, 3 regular nodes) with user-provided keys
        print("\n=== Creating Network Nodes ===")
        print("We will create 5 nodes in the network: User, Miner_1, Miner_2, Node_3, Node_4")
        print("You will need to provide prime numbers for each node to generate their cryptographic keys.")
        
        # Define node names
        node_names = ["User", "Miner_1", "Miner_2", "Node_3", "Node_4"]
        all_nodes = []
        
        # Get keys for all nodes
        for node_name in node_names:
            p, q = get_user_input_for_keys(node_name)
            public_key, private_key = CryptographicUtils.generate_keys_from_primes(p, q)
            
            print(f"\n=== Generated Keys for {node_name} ===")
            print(f"Public Key (n, e): {public_key}")
            print(f"Private Key (d): {private_key}")
            print("=" * 50)
            
            # Create appropriate node type
            if node_name == "User":
                node = Node(node_name, public_key, private_key)
            elif "Miner" in node_name:
                node = Miner(node_name, public_key, private_key)
            else:
                node = Node(node_name, public_key, private_key)
            
            all_nodes.append(node)
            blockchain.add_node(node)
        
        print(f"\nCreated network with 5 nodes: {', '.join(node_names)}")
        print(f"Number of miners in the network: {len(blockchain.miners)}")
        print("The network is initializing...")
        
        # Create genesis block with initial coin distribution
        blockchain.create_genesis_block()
    
    # Display initial network status
    blockchain.display_network_status()
    
    # Only allow transactions if we have private keys (fresh start)
    if not existing_data_loaded:
        # Transaction input loop
        print("\n=== Transaction Creation ===")
        print("You can now create transactions between any nodes in the network.")
        print("Each transaction will be digitally signed by the sender and verified before being added to the blockchain.")
        
        while True:
            try:
                print("\n" + "="*60)
                print("Available nodes and their public keys:")
                for i, node in enumerate(blockchain.nodes):
                    node_type = "Miner" if node.is_miner else "Node"
                    balance = node.get_balance()
                    print(f"{i+1}. {node.name} ({node_type}): {node.public_key}")
                    print(f"    Current Balance: {balance:.2f} coins")
                
                print("\nSelect SENDER by number (or 0 to finish):")
                sender_choice = int(input())
                
                if sender_choice == 0:
                    break
                
                if sender_choice < 1 or sender_choice > len(blockchain.nodes):
                    print("Invalid choice!")
                    continue
                
                sender_node = blockchain.nodes[sender_choice - 1]
                
                print(f"\nSelected sender: {sender_node.name}")
                print("Now select the recipient:")
                
                print("\nAvailable recipients:")
                for i, node in enumerate(blockchain.nodes):
                    if node != sender_node:  # Don't show sender as option
                        node_type = "Miner" if node.is_miner else "Node"
                        print(f"{i+1}. {node.name} ({node_type}): {node.public_key}")
                
                print("\nSelect RECIPIENT by number:")
                recipient_choice = int(input())
                
                if recipient_choice < 1 or recipient_choice > len(blockchain.nodes):
                    print("Invalid choice!")
                    continue
                
                recipient_node = blockchain.nodes[recipient_choice - 1]
                
                if recipient_node == sender_node:
                    print("Cannot send to the same node!")
                    continue
                
                amount = float(input(f"Enter amount to send from {sender_node.name} to {recipient_node.name}: "))
                
                if amount <= 0:
                    print("Please enter a positive amount!")
                    continue
                
                print(f"\nCreating transaction: {amount} coins from {sender_node.name} to {recipient_node.name}")
                print("Signing transaction with sender's private key...")
                
                # Create and sign transaction
                transaction = sender_node.create_transaction(recipient_node.public_key, amount)
                
                if transaction:
                    print(f"\nTransaction created successfully!")
                    print(f"Transaction ID: {transaction.transaction_id}")
                    print(f"Digital Signature: {transaction.signature}")
                    print(f"From: {sender_node.name} (Public Key: {sender_node.public_key})")
                    print(f"To: {recipient_node.name} (Public Key: {recipient_node.public_key})")
                    print(f"Amount: {amount}")
                    
                    # Verify transaction signature
                    if transaction.verify_transaction():
                        print("[SUCCESS] Transaction signature verified!")
                        blockchain.add_transaction_to_mempool(transaction)
                    else:
                        print("[ERROR] Transaction signature verification failed!")
                
            except ValueError:
                print("Please enter valid numbers!")
            except KeyboardInterrupt:
                print("\nExiting transaction creation...")
                break
        
        # Mining phase
        print("\n=== Mining Phase ===")
        print("Now we'll demonstrate the mining process where miners compete to add blocks to the blockchain.")
        
        while blockchain.mempool:
            print(f"\nThere are {len(blockchain.mempool)} transactions waiting to be mined.")
            input("Press Enter to start the next mining competition...")
            
            blockchain.mine_next_block()
            blockchain.display_network_status()
    
    # Final blockchain state
    print("\n=== Final Network Summary ===")
    if not existing_data_loaded:
        print("All transactions have been successfully mined and added to the blockchain!")
    blockchain.display_network_status()
    
    print("\n=== Complete Blockchain History ===")
    print("Here's a detailed view of every block that was created:")
    for i, block in enumerate(blockchain.nodes[0].blockchain):
        print(f"\nBlock {i}:")
        print(f"  Block Hash: {block.hash}")
        print(f"  Previous Block Hash: {block.previous_hash}")
        print(f"  Number of Transactions: {len(block.transactions)}")
        print(f"  Mining Nonce: {block.nonce}")
        
        for j, tx in enumerate(block.transactions):
            sender_name = "System" if tx.sender_public_key == (0, 0) else "Network Participant"
            print(f"    Transaction {j+1}: {sender_name} sent {tx.amount} coins")
    
    # Save blockchain state
    blockchain.save_blockchain()
    
    print("\nBlockchain simulation completed successfully!")
    print("The blockchain has been saved and all transactions have been processed.")
    print("Thank you for exploring this Bitcoin-style Proof of Work blockchain simulation!")

if __name__ == "__main__":
    main()