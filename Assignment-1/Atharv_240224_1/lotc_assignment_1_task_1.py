
import hashlib
import time
import json
import random
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

class Transaction:
    def __init__(self, sender: str, recipient: str, amount: float):
        """Initialize a transaction with sender, recipient, and amount."""
        self.sender = sender  # Sender's public key as a string
        self.recipient = recipient  # Recipient's public key as a string
        self.amount = amount
        self.signature = None

    def to_string(self) -> str:
        """Convert transaction to a string for hashing and display, without truncation."""
        return f"{self.sender}{self.recipient}{self.amount}"

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of transaction data."""
        return hashlib.sha256(self.to_string().encode()).hexdigest()

    def sign(self, private_key):
        """Sign the transaction using the sender's private key."""
        self.signature = private_key.sign(
            self.compute_hash().encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def verify(self, public_key) -> bool:
        """Verify the transaction's signature using the sender's public key."""
        try:
            public_key.verify(
                self.signature,
                self.compute_hash().encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False

class Block:
    def __init__(self, transactions: list, previous_hash: str, timestamp: float = None):
        """Initialize a block with transactions, previous hash, and optional timestamp."""
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of block data."""
        block_data = (
            f"{[t.to_string() for t in self.transactions]}"
            f"{self.previous_hash}{self.timestamp}{self.nonce}"
        )
        return hashlib.sha256(block_data.encode()).hexdigest()

    def mine(self, difficulty: int):
        """Mine the block by finding a nonce that produces a hash with 'difficulty' leading zeros."""
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.compute_hash()
        print(f"Mined block with hash: {self.hash}")

    def to_dict(self) -> dict:
        """Convert block to a dictionary for printing."""
        return {
            "hash": self.hash,
            "previous_hash": self.previous_hash,
            "transactions": [t.to_string() for t in self.transactions]
        }

class Blockchain:
    def __init__(self, genesis_block: Block):
        """Initialize blockchain with a shared genesis block and transaction pool."""
        self.blocks = [genesis_block]
        self.transaction_pool = []
        self.difficulty = 3  # Number of leading zeros required for PoW

    def add_transaction(self, transaction: Transaction):
        """Add a transaction to the mempool."""
        self.transaction_pool.append(transaction)

    def add_block(self, block: Block) -> bool:
        """Add a block to the blockchain if valid."""
        print(f"Attempting to add block with hash: {block.hash}")
        print(f"Block previous_hash: {block.previous_hash}")
        print(f"Last block hash in chain: {self.blocks[-1].hash}")
        if block.previous_hash == self.blocks[-1].hash:
            if self.verify_block(block):
                self.blocks.append(block)
                for tx in block.transactions:
                    if tx in self.transaction_pool:
                        self.transaction_pool.remove(tx)
                print(f"Block added successfully with hash: {block.hash}")
                return True
            else:
                print(f"Block verification failed for hash: {block.hash}")
        else:
            print(f"Invalid previous hash for block: {block.hash} (expected {self.blocks[-1].hash})")
        return False

    def verify_block(self, block: Block) -> bool:
        """Verify the block's hash and transaction signatures."""
        computed_hash = block.compute_hash()
        if block.hash != computed_hash:
            print(f"Block hash verification failed: computed {computed_hash}, expected {block.hash}")
            return False
        if not block.hash.startswith("0" * self.difficulty):
            print(f"Block hash does not meet difficulty requirement: {block.hash}")
            return False
        for tx in block.transactions:
            if tx.signature != b"reward":  # Skip verification for reward transactions
                try:
                    public_key = serialization.load_pem_public_key(tx.sender.encode())
                    if not tx.verify(public_key):
                        print(f"Transaction signature verification failed for transaction: {tx.to_string()}")
                        return False
                except ValueError as e:
                    print(f"Invalid public key in transaction: {str(e)}")
                    return False
        return True

    def print_blockchain(self):
        """Print all blocks in the blockchain with full details."""
        print("\nBlockchain:")
        if len(self.blocks) == 1:
            print("Only genesis block exists")
        for i, block in enumerate(self.blocks):
            print(f"Block {i}:")
            print(f"  Hash: {block.hash}")
            print(f"  Previous Hash: {block.previous_hash}")
            transactions_str = ", ".join(t.to_string() for t in block.transactions) or "None"
            print(f"  Transactions: {transactions_str}")

class Node:
    def __init__(self, node_id: str, genesis_block: Block):
        """Initialize a node with ID, key pair, balance, and shared genesis block."""
        self.node_id = node_id
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()
        self.public_key_str = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        self.blockchain = Blockchain(genesis_block)
        self.balance = 100.0  # Initial balance of 100 coins

    def create_transaction(self, recipient: str, amount: float, all_nodes: list) -> Transaction:
        """Create a transaction if balance is sufficient."""
        if amount <= 0:
            print(f"Error: Amount must be positive")
            return None
        if amount > self.balance:
            print(f"Error: {self.node_id} has insufficient balance ({self.balance})")
            return None
        transaction = Transaction(self.public_key_str, recipient, amount)
        transaction.sign(self.private_key)
        self.balance -= amount  # Subtract from sender
        for node in all_nodes:
            if node.public_key_str == recipient:
                node.balance += amount  # Add to recipient
                break
        print(f"Transaction created: {self.node_id} sends {amount} to recipient public key: {recipient}")
        print(f"Signature: {transaction.signature.hex()}")
        return transaction

class Miner(Node):
    def __init__(self, node_id: str, genesis_block: Block):
        """Initialize a miner, inheriting from Node."""
        super().__init__(node_id, genesis_block)

    def mine_block(self, transactions: list, previous_hash: str) -> Block:
        """Mine a block with given transactions and previous hash."""
        reward_tx = Transaction("network", self.public_key_str, 5.0)
        reward_tx.signature = b"reward"  # Fake signature for reward
        transactions = transactions + [reward_tx]
        self.balance += 5.0  # Add mining reward
        print(f"Starting to mine block with {len(transactions)} transactions, previous_hash: {previous_hash}")
        block = Block(transactions, previous_hash)
        block.mine(self.blockchain.difficulty)
        return block

def main():
    # Create a single genesis block with fixed timestamp
    genesis_timestamp = time.time()
    genesis_block = Block([], "0" * 64, timestamp=genesis_timestamp)
    print(f"Genesis block created with hash: {genesis_block.hash}")

    # Create 5 nodes and 2 miners with Indian names, sharing the genesis block
    nodes = [
        Node("Amit", genesis_block),
        Node("Priya", genesis_block),
        Node("Rahul", genesis_block),
        Node("Neha", genesis_block),
        Node("Vikram", genesis_block)
    ]
    miners = [
        Miner("Miner1", genesis_block),
        Miner("Miner2", genesis_block)
    ]
    all_nodes = nodes + miners

    while True:
        print("\nEnter sender name (Amit, Priya, Rahul, Neha, Vikram, or 'done' to finish):")
        sender_name = input().strip()
        if sender_name.lower() == "done":
            break
        sender_node = next((n for n in nodes if n.node_id == sender_name), None)
        if not sender_node:
            print("Invalid sender! Choose Amit, Priya, Rahul, Neha, or Vikram.")
            continue

        print("Enter recipient name (Amit, Priya, Rahul, Neha, Vikram):")
        recipient_name = input().strip()
        recipient_node = next((n for n in nodes if n.node_id == recipient_name), None)
        if not recipient_node:
            print("Invalid recipient! Choose Amit, Priya, Rahul, Neha, or Vikram.")
            continue
        if recipient_node == sender_node:
            print("Error: Sender and recipient cannot be the same.")
            continue

        print("Enter amount:")
        try:
            amount = float(input())
            transaction = sender_node.create_transaction(recipient_node.public_key_str, amount, all_nodes)
            if transaction:
                for node in all_nodes:
                    node.blockchain.add_transaction(transaction)
                miner = random.choice(miners)
                previous_hash = nodes[0].blockchain.blocks[-1].hash
                block = miner.mine_block([transaction], previous_hash)
                block_added = False
                for node in all_nodes:
                    if node.blockchain.add_block(block):
                        block_added = True
                    else:
                        print(f"Block verification failed for {node.node_id}'s blockchain")
                if not block_added:
                    print("Warning: Block was not added to any blockchain")
        except ValueError:
            print("Invalid amount! Enter a positive number.")

        print("\nContinue creating transactions and blocks? (yes/no):")
        if input().strip().lower() != "yes":
            break

    print("\nFinal balances:")
    for node in all_nodes:
        print(f"{node.node_id}: {node.balance}")

    for node in all_nodes:
        print(f"\n{node.node_id}'s Blockchain:")
        node.blockchain.print_blockchain()

if __name__ == "__main__":
    main()