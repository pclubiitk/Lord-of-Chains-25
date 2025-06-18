#Task 1
import hashlib
import random

# Transaction class to store transaction details
class Transaction():
    def __init__(self, pb_key,recipient_key, amount, signature):
        self.signature = signature
        self.pb_key = pb_key
        self.recipient_key = recipient_key
        self.amount =amount

# Function to mine a block 
def mine_block(block, difficulty=3):
    reward = 10
     # Randomly decide if this block is mined (for demo purposes)
    r = random.randint(1,1000)
    if (r%2==0):
        block.miner = True
        block.reward = True
        
    else:
        block.miner = False      
    
    # Proof-of-work: find a hash with required number of leading zeros
    target = "0" * difficulty
    while True:
        hash_data = f"{block.prev_hash}{block.data}{block.nonce}"
        computed_hash = compute_hash(hash_data)
        if computed_hash.startswith(target):
            block.hash = computed_hash
            block.miner = True
            break
        block.nonce += 1

# Block class to store block details
class Block:
    def __init__(self, pb_key,recepient, data,signature ,new_hash,  prev_hash, is_miner = False,nonce = 0, reward = False):
        self.pb_key = pb_key
        self.recepient = recepient
        self.data = data
        self.signature = signature
        self.hash = new_hash
        self.prev_hash = prev_hash
        self.miner = is_miner
        self.nonce = nonce
        self.reward = reward
        
# Function to compute hash of given data
def compute_hash(hash_data):
    hash_object = hashlib.sha1(hash_data.encode())
    hash_value = hash_object.hexdigest()
    return hash_value

# Function to verify a transaction's signature
def verify_transaction(block):
    value = f"{block.pb_key}{block.recepient}{block.data}"
    if block.signature == compute_hash(value):
        print("Transaction is verified")
        return True
    else:
        print("Transaction Failed")
        return False

def main():
    prev_hash = "0" *64
    difficulty = 3
    
    Blockchain = []
    transactions = []
    balances = {}
    pr_key = input("Enter your private key: ")
    pb_key = input("Enter your public key: ")
    while True:
        recepient = input("Enter Recipient Key or 'exit' to end: ")
        if recepient =="exit":
            break
        
        amount = int(input("Enter the Amount: "))

         # Create digital signature using hash
        d1 = f"{pb_key}{recepient}{amount}"
        signature = compute_hash(d1)
        print(f"Digital Signature: {signature}")
        # Create block and transaction objects
        block = Block(pb_key, recepient, amount, signature,"",prev_hash)
        txn = Transaction(pb_key, recepient, amount,signature)
        transactions.append(txn)
        
        mine_block(block, difficulty)
        prev_hash = block.hash
        
        if verify_transaction(block):
            Blockchain.append(block)

    # Calculate balances after all transactions
    for block in Blockchain:
        sender = block.pb_key
        recipient = block.recepient
        amount = block.data

        # Deduct amount from sender (initialize with 10000 if not present)
        balances[sender] = balances.get(sender, 10000) - amount

        # Add amount to recipient
        balances[recipient] = balances.get(recipient, 0) + amount
        #Add mining reward if block is mined
        if block.miner:
            balances[sender] = balances.get(sender, 0) + 10
            
    print("\nFinal Balances:")
    for address, balance in balances.items():
        print(f"{address[:6]}: {balance} coins")
        
    print("\n\n")
        
        

     # Print details of each block in the blockchain
    for i, block in enumerate(Blockchain):
        print(f"SENDER: {block.pb_key}")
        print(f"RECIEPENT: {block.recepient}")
        print(f"AMOUNT {block.data}")
        print(f"SIGNATURE {block.signature}")
        if block.miner ==True:
            print(f"STATUS: MINER")
            print("REWARD: 10")
        else:
            print(f"STATUS: NOT MINER")
            
        print("\n")

if __name__=='__main__':
    main()
        
        
        
