import hashlib
import json
import os
import time
from typing import List, Dict

class Transaction:
    """
    - sender_public_key: Public key of the sender
    - recipient_public_key: Public key of the recipient
    - amount: Amount to be transferred
    - signature: Digital signature created by sender's private key
    """
    def __init__(self, sender_public_key: str, recipient_public_key: str, amount: float, signature: str):
        self.sender_public_key = sender_public_key
        self.recipient_public_key = recipient_public_key
        self.amount = amount
        self.signature = signature

    def to_dict(self) -> Dict:
        return {
            'sender': self.sender_public_key,
            'recipient': self.recipient_public_key,
            'amount': self.amount,
            'signature': self.signature
        }


    def from_dict(data: Dict) -> 'Transaction':
        return Transaction(
            data['sender'], data['recipient'], data['amount'], data['signature']
        )


class Block:
    """
    - index: Position of the block in the chain
    - timestamp: Creation time of the block
    - transactions: List of Transaction objects
    - previous_hash: Hash of the previous block
    - nonce: The value found via Proof-of-Work
    - hash: SHA-256 hash of the block's contents
    """
    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        """Compute hash of the block's content including nonce."""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int):
        """
        Running Proof-of-Work algorithm to find a hash that starts with '0' * difficulty.
        """
        target = '0' * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.compute_hash()
class Blockchain:
    """
    Manages the chain of blocks, transaction pool, and balances.
    """
    def __init__(self, chain_file: str = 'blockchain.json', difficulty: int = 4, mining_reward: float = 50):
        self.chain_file = chain_file
        self.difficulty = difficulty
        self.mining_reward = mining_reward
        self.transaction_pool: List[Transaction] = []
        self.load_chain()

    def create_genesis_block(self):
        """Create the first block in the chain, with no transactions and previous_hash='0'."""
        genesis = Block(0, [], '0')
        genesis.hash = genesis.compute_hash()
        self.chain = [genesis]
        self.save_chain()

    def load_chain(self):
        """Load blockchain from file or create a new one if file not found."""
        if os.path.exists(self.chain_file):
            with open(self.chain_file, 'r') as f:
                data = json.load(f)
                self.chain = [self._block_from_dict(b) for b in data]
        else:
            self.create_genesis_block()

    def save_chain(self):
        """Save current blockchain to file."""
        with open(self.chain_file, 'w') as f:
            json.dump([self._block_to_dict(b) for b in self.chain], f, indent=4)

    def _block_to_dict(self, block: Block) -> Dict:
        return {
            'index': block.index,
            'timestamp': block.timestamp,
            'transactions': [tx.to_dict() for tx in block.transactions],
            'previous_hash': block.previous_hash,
            'nonce': block.nonce,
            'hash': block.hash
        }

    def _block_from_dict(self, data: Dict) -> Block:
        block = Block(data['index'], [], data['previous_hash'])
        block.timestamp = data['timestamp']
        block.transactions = [Transaction.from_dict(tx) for tx in data['transactions']]
        block.nonce = data['nonce']
        block.hash = data['hash']
        return block

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction):
        """Add a transaction to the pool after signature verification."""
        # NOTE: For demo, we assume signature is valid.
        self.transaction_pool.append(transaction)

    def mine_pending_transactions(self, miner_address: str):
        """
        Create new block(s) from pending transactions,
        include mining reward, and add to chain.
        """
        # add mining reward transaction
        reward_tx = Transaction('SYSTEM', miner_address, self.mining_reward, '')
        self.transaction_pool.append(reward_tx)

        # split transactions into chunks (e.g., max 2 per block)
        chunk_size = 2
        while self.transaction_pool:
            chunk = self.transaction_pool[:chunk_size]
            self.transaction_pool = self.transaction_pool[chunk_size:]

            new_block = Block(self.get_last_block().index + 1, chunk, self.get_last_block().hash)
            print(f"Miner {miner_address} is mining block {new_block.index}...")
            new_block.mine_block(self.difficulty)
            print(f"Block {new_block.index} mined with hash: {new_block.hash}\n")
            self.chain.append(new_block)

        self.save_chain()

    def get_balance(self, address: str) -> float:
        """Calculate balance for an address by iterating over all blocks."""
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender_public_key == address:
                    balance -= tx.amount
                if tx.recipient_public_key == address:
                    balance += tx.amount
        return balance
def sign_transaction(private_key: str, transaction_data: str) -> str:
    """
    Mock digital signature: hash of private_key + transaction_data.
    """
    return hashlib.sha256((private_key + transaction_data).encode()).hexdigest()


def main():
    user_public = input("Enter your public key: ")
    user_private = input("Enter your private key (for signing): ")
    recipient = input("Enter recipient's public key: ")
    amount = float(input("Enter amount: "))
    # build and sign transaction
    tx_data = f"{user_public}->{recipient}:{amount}"
    signature = sign_transaction(user_private, tx_data)
    transaction = Transaction(user_public, recipient, amount, signature)
    print(f"Digital signature of transaction: {signature}\n")
    bc = Blockchain()
    bc.add_transaction(transaction)
    more = input("Add more transactions? (y/n): ")
    while more.lower() == 'y':
        sender = input("Enter sender's public key: ")
        rec = input("Enter recipient's public key: ")
        amt = float(input("Enter amount: "))
        data = f"{sender}->{rec}:{amt}"
        sig = sign_transaction(user_private if sender==user_public else '', data)
        tx = Transaction(sender, rec, amt, sig)
        print(f"Digital signature: {sig}\n")
        bc.add_transaction(tx)
        more = input("Add more transactions? (y/n): ")
    # simulate two miners competing
    miner_keys = ["miner1_pub", "miner2_pub"]
    for m in miner_keys:
        print(f"Miner {m} starting mining competition...")
        bc.mine_pending_transactions(m)
    # display balances
    print("\nBalances:")
    participants = [user_public, recipient] + miner_keys
    for p in participants:
        print(f"Balance of {p}: {bc.get_balance(p)}")

if __name__ == '__main__':
    main()