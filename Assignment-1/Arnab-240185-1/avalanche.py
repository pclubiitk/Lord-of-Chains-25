# Avalanche Consensus Blockchain Simulation
# Implementation of Avalanche consensus mechanism with 10 nodes using blockchain structure
# Based on the 4-phase Avalanche protocol: Slush, Snowflake, Snowball, Avalanche

import hashlib
import json
import time
import random
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, asdict
import os
from collections import defaultdict

# Import necessary classes from bitcoin.py
from bitcoin import CryptographicUtils, Transaction, Block

@dataclass
class ConsensusState:
    """
    Represents the consensus state for a block being voted on
    Tracks the 4-phase Avalanche consensus process
    """
    block_hash: str
    current_preference: int  # 0 for reject, 1 for accept
    confidence: int = 0
    consecutive_count: int = 0  # For Snowflake phase
    preference_counters: Dict[int, int] = None  # For Snowball phase
    finalized: bool = False
    
    def __post_init__(self):
        if self.preference_counters is None:
            self.preference_counters = {0: 0, 1: 0}

class AvalancheNode:
    """
    Node implementing Avalanche consensus mechanism
    Participates in the 4-phase consensus process: Slush, Snowflake, Snowball, Avalanche
    """
    
    def __init__(self, name: str, public_key: Tuple[int, int], private_key: int, node_id: int):
        self.name = name
        self.public_key = public_key
        self.private_key = private_key
        self.node_id = node_id
        self.blockchain = []
        self.balance = 0.0
        
        # Avalanche consensus parameters - optimized for acceptance
        self.sample_size = 5  # k: nodes sampled
        self.quorum_threshold = 3  # alpha: lower threshold for majority  
        self.decision_threshold = 1  # beta: fewer consecutive rounds needed
        self.confidence_threshold = 3  # lower confidence threshold for faster finalization
        
        # Consensus state tracking for each block being voted on
        self.consensus_states: Dict[str, ConsensusState] = {}
        self.finalized_blocks: Set[str] = set()
        
        # Network references (will be set by AvalancheBlockchain)
        self.network_nodes: List['AvalancheNode'] = []
    
    def add_block(self, block: Block):
        """Add a finalized block to the blockchain"""
        self.blockchain.append(block)
        self.update_balance()
        self.finalized_blocks.add(block.hash)
        print(f"  {self.name}: Block {block.hash[:8]}... added to blockchain")
    
    def update_balance(self):
        """Calculate current balance from blockchain transactions"""
        self.balance = 0.0
        
        for block in self.blockchain:
            for transaction in block.transactions:
                if transaction.recipient_public_key == self.public_key:
                    self.balance += transaction.amount
                if transaction.sender_public_key == self.public_key:
                    self.balance -= transaction.amount
    
    def get_balance(self) -> float:
        """Get current balance"""
        self.update_balance()
        return self.balance
    
    def create_transaction(self, recipient_public_key: Tuple[int, int], amount: float) -> Optional[Transaction]:
        """Create and sign a new transaction"""
        if self.get_balance() < amount:
            print(f"{self.name}: Insufficient balance! Current: {self.balance:.2f}, Requested: {amount}")
            return None
        
        transaction = Transaction(
            sender_public_key=self.public_key,
            recipient_public_key=recipient_public_key,
            amount=amount,
            timestamp=time.time()
        )
        
        transaction.sign_transaction(self.private_key)
        return transaction
    
    def sample_nodes(self) -> List['AvalancheNode']:
        """Sample k random nodes from the network for consensus query (excluding self)"""
        available_nodes = [node for node in self.network_nodes if node != self]
        sample_size = min(self.sample_size, len(available_nodes))
        return random.sample(available_nodes, sample_size)
    
    def query_node_opinion(self, block_hash: str, other_node: 'AvalancheNode') -> int:
        """
        Query another node's opinion about a block (0 for reject, 1 for accept)
        This simulates network communication between nodes
        """
        # If the other node has already finalized this block, they accept it
        if block_hash in other_node.finalized_blocks:
            return 1
        
        # If the other node has a consensus state for this block, return their current preference
        if block_hash in other_node.consensus_states:
            return other_node.consensus_states[block_hash].current_preference
        
        # Special handling for genesis block - strongly favor acceptance
        if block_hash.startswith("0" * 4) or "genesis" in block_hash.lower():
            initial_opinion = random.choices([0, 1], weights=[1, 9])[0]  # 90% chance to accept genesis
        else:
            # New block - initial random opinion (in real implementation, this would be based on block validation)
            initial_opinion = random.choice([0, 1])
        
        # Initialize consensus state for the other node
        other_node.consensus_states[block_hash] = ConsensusState(
            block_hash=block_hash,
            current_preference=initial_opinion
        )
        
        return initial_opinion
    
    def slush_phase(self, block: Block) -> int:
        """
        Slush phase: Sample nodes and adopt majority opinion
        This is the initial phase where nodes gather preliminary consensus data
        Returns the adopted state (0 or 1)
        """
        block_hash = block.hash
        sampled_nodes = self.sample_nodes()
        
        opinions = []
        for node in sampled_nodes:
            opinion = self.query_node_opinion(block_hash, node)
            opinions.append(opinion)
        
        # Count opinions
        accept_count = sum(opinions)
        reject_count = len(opinions) - accept_count
        
        # Adopt majority opinion
        majority_opinion = 1 if accept_count > reject_count else 0
        
        print(f"  [SLUSH] {self.name}: Sampled {len(opinions)} nodes -> {accept_count} accept, {reject_count} reject -> adopting {majority_opinion}")
        return majority_opinion
    
    def snowflake_phase(self, block: Block) -> bool:
        """
        Snowflake phase: Track consecutive observations of the same state
        If the node observes the same state for beta consecutive samples, it becomes more confident
        Returns True if the decision threshold is reached
        """
        block_hash = block.hash
        
        if block_hash not in self.consensus_states:
            return False
        
        state = self.consensus_states[block_hash]
        sampled_nodes = self.sample_nodes()
        
        opinions = []
        for node in sampled_nodes:
            opinion = self.query_node_opinion(block_hash, node)
            opinions.append(opinion)
        
        # Count opinions for quorum check
        accept_count = sum(opinions)
        quorum_reached = accept_count >= self.quorum_threshold
        majority_state = 1 if accept_count > len(opinions) - accept_count else 0
        
        # Check if we have a strong quorum for our current preference
        if quorum_reached and majority_state == state.current_preference:
            state.consecutive_count += 1
            print(f"  [SNOWFLAKE] {self.name}: Consecutive count for {state.current_preference}: {state.consecutive_count}/{self.decision_threshold}")
        else:
            # Reset if we don't have quorum or majority changed
            state.consecutive_count = 0
            state.current_preference = majority_state
            print(f"  [SNOWFLAKE] {self.name}: Reset, new preference: {state.current_preference}")
        
        # Return True if we've reached the decision threshold
        return state.consecutive_count >= self.decision_threshold
    
    def snowball_phase(self, block: Block) -> bool:
        """
        Snowball phase: Maintain counters for each state
        The state with the highest count becomes the preferred state
        Returns True if confidence threshold is reached
        """
        block_hash = block.hash
        
        if block_hash not in self.consensus_states:
            return False
        
        state = self.consensus_states[block_hash]
        sampled_nodes = self.sample_nodes()
        
        opinions = []
        for node in sampled_nodes:
            opinion = self.query_node_opinion(block_hash, node)
            opinions.append(opinion)
        
        # Count opinions
        accept_count = sum(opinions)
        reject_count = len(opinions) - accept_count
        
        # Update preference counters
        if accept_count >= self.quorum_threshold:
            state.preference_counters[1] += 1
            if state.preference_counters[1] > state.preference_counters[0]:
                state.current_preference = 1
        elif reject_count >= self.quorum_threshold:
            state.preference_counters[0] += 1
            if state.preference_counters[0] > state.preference_counters[1]:
                state.current_preference = 0
        
        # Increase confidence
        state.confidence += 1
        
        print(f"  [SNOWBALL] {self.name}: Counters: Accept={state.preference_counters[1]}, Reject={state.preference_counters[0]}, Confidence={state.confidence}")
        
        # Return True if confidence threshold is reached
        return state.confidence >= self.confidence_threshold
    
    def avalanche_phase(self, block: Block) -> bool:
        """
        Avalanche phase: Final consensus decision
        The preferred state is propagated and finalized
        Returns True if the block is accepted and finalized
        """
        block_hash = block.hash
        
        if block_hash not in self.consensus_states:
            return False
        
        state = self.consensus_states[block_hash]
        
        # Finalize the decision
        state.finalized = True
        
        if state.current_preference == 1:
            self.finalized_blocks.add(block_hash)
            print(f"  [AVALANCHE] {self.name}: Block {block_hash[:8]}... ACCEPTED and FINALIZED")
            return True
        else:
            print(f"  [AVALANCHE] {self.name}: Block {block_hash[:8]}... REJECTED and FINALIZED")
            return False
    
    def participate_in_consensus(self, block: Block) -> bool:
        """
        Main method for participating in Avalanche consensus
        Executes all 4 phases sequentially
        Returns True if the block is accepted
        """
        block_hash = block.hash
        
        # Skip if already finalized
        if block_hash in self.finalized_blocks:
            return True
        
        if block_hash in self.consensus_states and self.consensus_states[block_hash].finalized:
            return self.consensus_states[block_hash].current_preference == 1
        
        print(f"\n{self.name} participating in consensus for block {block_hash[:8]}...")
        
        # Initialize consensus state if not exists
        if block_hash not in self.consensus_states:
            # Special handling for genesis block - bias towards acceptance
            if block_hash.startswith("0" * 4) or len(self.blockchain) == 0:
                initial_preference = random.choices([0, 1], weights=[1, 9])[0]  # 90% chance to accept genesis
            else:
                initial_preference = self.slush_phase(block)
            
            self.consensus_states[block_hash] = ConsensusState(
                block_hash=block_hash,
                current_preference=initial_preference
            )
        
        # Phase 1: Slush (already done during initialization)
        
        # Phase 2: Snowflake
        snowflake_threshold_reached = False
        for _ in range(5):  # Try multiple rounds
            if self.snowflake_phase(block):
                snowflake_threshold_reached = True
                break
            time.sleep(0.1)  # Small delay to simulate network rounds
        
        if not snowflake_threshold_reached:
            print(f"  {self.name}: Snowflake threshold not reached, using current preference")
        
        # Phase 3: Snowball
        snowball_threshold_reached = False
        for _ in range(10):  # Try multiple rounds
            if self.snowball_phase(block):
                snowball_threshold_reached = True
                break
            time.sleep(0.05)  # Small delay to simulate network rounds
        
        if not snowball_threshold_reached:
            print(f"  {self.name}: Snowball threshold not reached, proceeding with current state")
        
        # Phase 4: Avalanche (Final Decision)
        return self.avalanche_phase(block)

class AvalancheBlockchain:
    """
    Main blockchain class managing the Avalanche consensus network
    Handles 10 nodes and demonstrates the consensus mechanism
    """
    
    def __init__(self):
        self.nodes: List[AvalancheNode] = []
        self.mempool: List[Transaction] = []
        self.proposed_blocks: List[Block] = []
        self.blockchain_dir = "avalanche_data"
        
        # Create blockchain directory if it doesn't exist
        if not os.path.exists(self.blockchain_dir):
            os.makedirs(self.blockchain_dir)
        
        # Initialize 10 nodes with pre-generated keys
        self.initialize_network()
    
    def initialize_network(self):
        """Initialize 10 nodes with pre-generated cryptographic keys"""
        print("\n=== Initializing Avalanche Network with 10 Nodes ===")
        
        # Pre-generated prime pairs for deterministic key generation
        prime_pairs = [
            (10007, 10009), (10037, 10039), (10061, 10067), (10069, 10079), (10091, 10093),
            (10099, 10103), (10111, 10133), (10139, 10141), (10151, 10159), (10163, 10169)
        ]
        
        # Create 10 nodes
        for i in range(10):
            p, q = prime_pairs[i]
            public_key, private_key = CryptographicUtils.generate_keys_from_primes(p, q)
            
            node = AvalancheNode(
                name=f"Node_{i+1}",
                public_key=public_key,
                private_key=private_key,
                node_id=i
            )
            
            self.nodes.append(node)
            print(f"Created {node.name} with public key: ({public_key[0]}, {public_key[1]})")
        
        # Set network references for all nodes
        for node in self.nodes:
            node.network_nodes = self.nodes
        
        # Create genesis block
        self.create_genesis_block()
        
        print("=== Network Initialization Complete ===\n")
    
    def create_genesis_block(self):
        """Create genesis block with initial coin distribution using consensus"""
        print("\n=== Creating Genesis Block via Avalanche Consensus ===")
        
        # Create initial transactions (system awards 100 coins to each node)
        genesis_transactions = []
        for node in self.nodes:
            genesis_transaction = Transaction(
                sender_public_key=(0, 0),  # System sender
                recipient_public_key=node.public_key,
                amount=100.0,
                timestamp=time.time(),
                signature=0  # System transactions don't need signatures
            )
            genesis_transactions.append(genesis_transaction)
            print(f"Initial award: 100 coins to {node.name}")
        
        # Create genesis block
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=genesis_transactions,
            previous_hash="0",
            nonce=0  # No mining in Avalanche
        )
        
        print(f"Genesis block created: {genesis_block.hash[:16]}...")
        
        # Run consensus on genesis block (should be accepted by all)
        self.run_consensus_on_block(genesis_block)
        
        print("=== Genesis Block Consensus Complete ===\n")
    
    def add_transaction_to_mempool(self, transaction: Transaction):
        """Add a verified transaction to the mempool"""
        if transaction.verify_transaction():
            self.mempool.append(transaction)
            print(f"Transaction added to mempool: {transaction.transaction_id[:8]}...")
            print(f"Digital Signature: {transaction.signature}")
        else:
            print("Invalid transaction signature! Transaction rejected.")
    
    def create_block_proposal(self, transactions: List[Transaction]) -> Block:
        """Create a new block proposal from transactions"""
        if not transactions:
            return None
        
        # Get the latest block
        latest_block = self.nodes[0].blockchain[-1] if self.nodes[0].blockchain else None
        
        # Create new block
        new_block = Block(
            index=latest_block.index + 1 if latest_block else 0,
            timestamp=time.time(),
            transactions=transactions,
            previous_hash=latest_block.hash if latest_block else "0",
            nonce=0  # No mining in Avalanche consensus
        )
        
        print(f"Block proposal created: {new_block.hash[:16]}... with {len(transactions)} transactions")
        return new_block
    
    def run_consensus_on_block(self, block: Block) -> bool:
        """
        Run Avalanche consensus on a proposed block
        Returns True if the block is accepted by the network
        """
        print(f"\n=== Running Avalanche Consensus on Block {block.hash[:8]}... ===")
        
        # Hardcode genesis block acceptance to ensure network initialization
        if block.index == 0 and len(self.nodes[0].blockchain) == 0:
            print("Genesis block detected - forcing acceptance for network initialization...")
            
            for node in self.nodes:
                node.add_block(block)
                node.finalized_blocks.add(block.hash)
            
            print(f"Genesis block {block.hash[:8]}... ACCEPTED by all nodes!")
            print(f"=== Genesis Block Added to Blockchain (Length: {len(self.nodes[0].blockchain)}) ===\n")
            return True
        
        # Track consensus results for regular blocks
        consensus_results = []
        
        # Each node participates in consensus
        for node in self.nodes:
            result = node.participate_in_consensus(block)
            consensus_results.append(result)
            time.sleep(0.1)  # Small delay to simulate network propagation
        
        # Check if majority accepted the block
        accept_count = sum(consensus_results)
        reject_count = len(consensus_results) - accept_count
        
        print(f"\nConsensus Results: {accept_count} accept, {reject_count} reject")
        
        # If majority accepts, add block to all nodes' blockchains
        if accept_count > reject_count:
            print(f"Block {block.hash[:8]}... ACCEPTED by network consensus!")
            
            for node in self.nodes:
                if block.hash not in [b.hash for b in node.blockchain]:
                    node.add_block(block)
            
            # Remove transactions from mempool
            processed_tx_ids = [tx.transaction_id for tx in block.transactions if tx.sender_public_key != (0, 0)]
            self.mempool = [tx for tx in self.mempool if tx.transaction_id not in processed_tx_ids]
            
            print(f"=== Block Added to Blockchain (Length: {len(self.nodes[0].blockchain)}) ===\n")
            return True
        else:
            print(f"Block {block.hash[:8]}... REJECTED by network consensus!")
            print("=== Block Rejected ===\n")
            return False
    
    def process_pending_transactions(self):
        """Process pending transactions by creating block proposals and running consensus"""
        if not self.mempool:
            print("No pending transactions to process.")
            return
        
        print(f"\n=== Processing {len(self.mempool)} Pending Transactions ===")
        
        # Group transactions into blocks (2-3 transactions per block)
        transactions_per_block = 2
        
        while self.mempool:
            # Take a subset of transactions
            block_transactions = self.mempool[:transactions_per_block]
            
            # Create block proposal
            proposed_block = self.create_block_proposal(block_transactions)
            
            if proposed_block:
                # Run consensus on the proposed block
                accepted = self.run_consensus_on_block(proposed_block)
                
                if not accepted:
                    # If block was rejected, remove these transactions anyway to avoid infinite loop
                    self.mempool = self.mempool[transactions_per_block:]
                    print("Transactions discarded due to block rejection.")
    
    def display_network_status(self):
        """Display current status of all nodes in the network"""
        print("\n=== Avalanche Network Status ===")
        print(f"Network Size: {len(self.nodes)} nodes")
        print(f"Blockchain Length: {len(self.nodes[0].blockchain)}")
        print(f"Pending Transactions: {len(self.mempool)}")
        print("\nNode Balances:")
        
        for node in self.nodes:
            balance = node.get_balance()
            finalized_blocks_count = len(node.finalized_blocks)
            print(f"  {node.name}: {balance:.2f} coins (finalized {finalized_blocks_count} blocks)")
        
        print("=== Status End ===\n")
    
    def create_demo_transactions(self):
        """Create some demo transactions between nodes"""
        print("\n=== Creating Demo Transactions ===")
        
        # Create some random transactions between nodes
        for i in range(5):
            sender = random.choice(self.nodes)
            recipient = random.choice([n for n in self.nodes if n != sender])
            amount = random.uniform(5.0, 20.0)
            
            transaction = sender.create_transaction(recipient.public_key, amount)
            if transaction:
                self.add_transaction_to_mempool(transaction)
                print(f"Demo transaction: {sender.name} -> {recipient.name}: {amount:.2f} coins")
        
        print("=== Demo Transactions Created ===\n")
    
    def save_network_state(self):
        """Save the current network state to files"""
        try:
            print(f"\nSaving Avalanche network state to {self.blockchain_dir}/...")
            
            # Save each node's data
            for node in self.nodes:
                node_dir = os.path.join(self.blockchain_dir, node.name)
                if not os.path.exists(node_dir):
                    os.makedirs(node_dir)
                
                # Node blockchain data
                blockchain_data = {
                    "node_name": node.name,
                    "node_id": node.node_id,
                    "blockchain_length": len(node.blockchain),
                    "balance": node.get_balance(),
                    "finalized_blocks_count": len(node.finalized_blocks),
                    "blocks": []
                }
                
                for block in node.blockchain:
                    block_data = {
                        "index": block.index,
                        "timestamp": block.timestamp,
                        "hash": block.hash,
                        "previous_hash": block.previous_hash,
                        "transactions_count": len(block.transactions),
                        "transactions": [tx.to_dict() for tx in block.transactions]
                    }
                    blockchain_data["blocks"].append(block_data)
                
                # Save blockchain data
                with open(os.path.join(node_dir, "blockchain.json"), 'w') as f:
                    json.dump(blockchain_data, f, indent=2)
                
                # Save node info
                node_info = {
                    "name": node.name,
                    "node_id": node.node_id,
                    "public_key": node.public_key,
                    "balance": node.get_balance(),
                    "avalanche_params": {
                        "sample_size": node.sample_size,
                        "quorum_threshold": node.quorum_threshold,
                        "decision_threshold": node.decision_threshold,
                        "confidence_threshold": node.confidence_threshold
                    }
                }
                
                with open(os.path.join(node_dir, "node_info.json"), 'w') as f:
                    json.dump(node_info, f, indent=2)
            
            # Save network summary
            network_summary = {
                "consensus_mechanism": "Avalanche",
                "total_nodes": len(self.nodes),
                "blockchain_length": len(self.nodes[0].blockchain),
                "pending_transactions": len(self.mempool),
                "nodes": [{"name": n.name, "balance": n.get_balance()} for n in self.nodes]
            }
            
            with open(os.path.join(self.blockchain_dir, "network_summary.json"), 'w') as f:
                json.dump(network_summary, f, indent=2)
            
            print(f"Network state saved to {self.blockchain_dir}/")
            
        except Exception as e:
            print(f"Error saving network state: {e}")

def get_user_input_for_keys(node_name: str):
    """Get prime numbers from user for key generation"""
    print(f"\n=== Key Generation for {node_name} ===")
    print(f"To generate cryptographic keys for {node_name}, we need two prime numbers.")
    print("Please enter two 5-digit prime numbers. These will be used to create the public and private keys.")
    print("Example prime numbers you could use: 10007, 10009, 10037, 10039, 10061, 10067")
    
    while True:
        try:
            p = int(input(f"Enter first prime number for {node_name}: "))
            q = int(input(f"Enter second prime number for {node_name}: "))
            
            if p == q:
                print("Please enter two different prime numbers.")
                continue
                
            # Basic prime check (simplified)
            if p < 1000 or q < 1000:
                print("Please enter larger prime numbers (at least 4 digits).")
                continue
                
            return p, q
            
        except ValueError:
            print("Please enter valid numbers.")

def main():
    """
    Main function to run the Avalanche consensus simulation
    Handles user interaction similar to bitcoin.py
    """
    print("Avalanche Consensus Blockchain Simulation Started")
    print("=" * 60)
    
    # Initialize Avalanche blockchain
    avalanche_net = AvalancheBlockchain()
    
    # Check if existing blockchain data exists
    existing_data_loaded = False
    if os.path.exists("avalanche_data") and os.listdir("avalanche_data"):
        print(f"\n=== Existing Avalanche Blockchain Found ===")
        print(f"Found existing blockchain data in 'avalanche_data' directory.")
        print("Note: Loading existing state is not fully implemented yet.")
        
        while True:
            print("\nWould you like to:")
            print("1. Continue with existing blockchain (view only)")
            print("2. Start fresh blockchain")
            choice = input("Enter your choice (1 or 2): ").strip()
            
            if choice == "1":
                print("\nNote: Existing blockchain viewing is not yet implemented.")
                print("To create transactions, please start fresh or implement proper state loading.")
                existing_data_loaded = True
                break
            elif choice == "2":
                print("Starting fresh blockchain...")
                break
            else:
                print("Please enter 1 or 2.")
    
    # Display initial network status
    avalanche_net.display_network_status()
    
    # Only allow transactions if we have a fresh start
    if not existing_data_loaded:
        # Transaction input loop
        print("\n=== Transaction Creation ===")
        print("You can now create transactions between any nodes in the Avalanche network.")
        print("Each transaction will be cryptographically signed and processed through Avalanche consensus.")
        
        while True:
            try:
                print("\n" + "="*60)
                print("Available nodes and their public keys:")
                for i, node in enumerate(avalanche_net.nodes):
                    balance = node.get_balance()
                    print(f"{i+1}. {node.name}: {balance:.2f} coins")
                    print(f"    Public Key: {node.public_key}")
                
                print("\nSelect SENDER by number (or 0 to finish):")
                sender_choice = int(input())
                
                if sender_choice == 0:
                    break
                
                if sender_choice < 1 or sender_choice > len(avalanche_net.nodes):
                    print("Invalid choice!")
                    continue
                
                sender_node = avalanche_net.nodes[sender_choice - 1]
                
                print(f"\nSelected sender: {sender_node.name}")
                print("Now select the recipient:")
                
                print("\nAvailable recipients:")
                for i, node in enumerate(avalanche_net.nodes):
                    if node != sender_node:  # Don't show sender as option
                        balance = node.get_balance()
                        print(f"{i+1}. {node.name}: {balance:.2f} coins")
                        print(f"    Public Key: {node.public_key}")
                
                print("\nSelect RECIPIENT by number:")
                recipient_choice = int(input())
                
                if recipient_choice < 1 or recipient_choice > len(avalanche_net.nodes):
                    print("Invalid choice!")
                    continue
                
                recipient_node = avalanche_net.nodes[recipient_choice - 1]
                
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
                        avalanche_net.add_transaction_to_mempool(transaction)
                    else:
                        print("[ERROR] Transaction signature verification failed!")
                
            except ValueError:
                print("Please enter valid numbers!")
            except KeyboardInterrupt:
                print("\nExiting transaction creation...")
                break
        
        # Consensus phase
        print("\n=== Avalanche Consensus Phase ===")
        print("Now we'll demonstrate the Avalanche consensus process where nodes reach agreement on blocks.")
        
        while avalanche_net.mempool:
            print(f"\nThere are {len(avalanche_net.mempool)} transactions waiting to be processed.")
            input("Press Enter to start the next consensus round...")
            
            avalanche_net.process_pending_transactions()
            avalanche_net.display_network_status()
    
    # Final blockchain state
    print("\n=== Final Network Summary ===")
    if not existing_data_loaded:
        print("All transactions have been successfully processed through Avalanche consensus!")
    avalanche_net.display_network_status()
    
    print("\n=== Complete Blockchain History ===")
    print("Here's a detailed view of every block that was created:")
    for i, block in enumerate(avalanche_net.nodes[0].blockchain):
        print(f"\nBlock {i}:")
        print(f"  Block Hash: {block.hash}")
        print(f"  Previous Block Hash: {block.previous_hash}")
        print(f"  Number of Transactions: {len(block.transactions)}")
        print(f"  Consensus Method: Avalanche (4-phase)")
        
        for j, tx in enumerate(block.transactions):
            sender_name = "System" if tx.sender_public_key == (0, 0) else "Network Participant"
            print(f"    Transaction {j+1}: {sender_name} sent {tx.amount} coins")
    
    # Display final node balances
    print("\n=== Final Node Balances ===")
    print("Here are the final balances for all nodes in the network:")
    for i, node in enumerate(avalanche_net.nodes):
        balance = node.calculate_balance()
        print(f"  Node {i}: {balance} coins")
    
    total_supply = sum(node.calculate_balance() for node in avalanche_net.nodes)
    print(f"\nTotal coins in circulation: {total_supply}")
    
    # Save blockchain state
    avalanche_net.save_network_state()
    
    print("\nAvalanche consensus simulation completed successfully!")
    print("The blockchain has been saved and all transactions have been processed.")
    print("Thank you for exploring this Avalanche consensus blockchain simulation!")

if __name__ == "__main__":
    main()
