import threading
from time import time
from pprint import pprint
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import random


all_node = []
all_miners = []

def get_name(node):
    return node.name

class Node():
    def __init__(self, name, block_chain):
        key = RSA.generate(2048)
        self.private_key = key
        self.public_key = key.publickey()
        self.name = name
        self.block_chain = block_chain
        self.balance = 1000
        all_node.append(self)

    def __repr__(self):
        return f'(name:{self.name},balance:{self.balance},public_key:{self.public_key})'

    def make_transaction(self, recipient, ammount, fee):
        if (recipient in list(map(get_name, all_node))):
            if ammount<0:
                print("You cann't take money from other without their permission")
                return
            elif ammount+fee>self.balance:
                print("You have insufficient balance to make this transaction")
                return



            msg = f"{self.public_key} sends {ammount} to {recipient}"
            hash_obj = SHA256.new(msg.encode('utf-8'))  # Added encode()
            signature = pkcs1_15.new(self.private_key).sign(hash_obj)

            self.block_chain.create_block(self, signature, f"{self.public_key} sends {ammount} to {recipient}",fee)
            self.balance -= ammount+fee
            for node in all_node:
                if(node.name==recipient):
                    node.balance+=ammount
        else:
            all_node.append(Node(recipient, self.block_chain))
            print("new node created")

            #extra protection
            if ammount<0:
                print("You cann't take money from other without their permission")
                return
            elif ammount+fee>self.balance:
                print("You have insufficient balance to make this transaction")
                return


            msg = f"{self.public_key} sends {ammount} to {recipient}"
            hash_obj = SHA256.new(msg.encode('utf-8'))  # Added encode()
            signature = pkcs1_15.new(self.private_key).sign(hash_obj)

            if(self.balance<ammount):
                print("This node cann't make such payment")

            self.block_chain.create_block(self, signature, f"{self.public_key} sends {ammount} to {recipient}")
            self.balance += ammount

class Miner(Node):
    def __init__(self, name, block_chain):
        super().__init__(name, block_chain)
        all_miners.append(self)
        
    def mine_block(self, block_template, difficulty, stop_event, result_lock, winning_block):
        i = 0
        block = block_template.copy()
        
        while not stop_event.is_set():
            block['nonce'] = i
            # Create hash of all fields except 'hash' itself
            block_str = str({k: v for k, v in block.items() if k != 'hash'})
            _hash = hashlib.sha256(block_str.encode('utf-8')).hexdigest()
            
            if _hash[:difficulty] == '0'*difficulty:
                with result_lock:  # Critical section
                    if not stop_event.is_set():  # Re-check after acquiring lock
                        block['hash'] = _hash
                        block['miner'] = self
                        winning_block.append(block)
                        stop_event.set()
                        return
            i += 1

class Blockchain():
    def __init__(self):
        self.blocks = []
        self.__secret = ''
        self.__difficulty = 4
        self.lock = threading.Lock()  # For thread-safe block addition
        
        # Initialize secret()
        if (random.uniform(0,1)<0.5):
            i = 0
        else:
            i=random.randint(1,100)
        secret_string = '/*SECRET*/'
        while True:
            _hash = hashlib.sha256(str(secret_string+str(i)).encode('utf-8')).hexdigest()
            if _hash[:self.__difficulty] == '0'*self.__difficulty:
                self.__secret = _hash
                break
            i += 1
    
    def create_block(self, sender: Node, signature, information: str, fee):
        # Verify signature first
        hash_obj = SHA256.new(information.encode('utf-8'))  # Added encode()
        try:
            pkcs1_15.new(sender.public_key).verify(hash_obj, signature)
            print("Signature is valid.")
        except (ValueError, TypeError):
            print("Signature is invalid. Cannot generate the block")
            return
        
        if (fee<0):
            print("fee must be greater than 0")
            return

        # Create block structure
        block_template = {
            'index': len(self.blocks),
            'sender': sender.name,
            'timestamp': time(),
            'info': information,
            'signature': signature.hex(),
            'previous_hash': self.__secret if not self.blocks else self.blocks[-1]['hash'],
            'fee':fee
        }
        if not all_miners:
            print("no miners exist to validate your block")
            return

        # Mining coordination
        stop_event = threading.Event()
        result_lock = self.lock
        winning_block = []  # Will contain at most 1 block

        # Start mining threads
        threads = []
        for miner in all_miners:
            t = threading.Thread(
                target=miner.mine_block,
                args=(block_template, self.__difficulty, stop_event, result_lock, winning_block)
            )
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join(timeout=60)  # Prevent indefinite hanging

        # Process result
        if winning_block:
            self.blocks.append(winning_block[0])
            print(f"Block mined by {winning_block[0]['miner']}")
            for miner in all_miners:
                if miner.name == winning_block[0]['miner'].name:
                    miner.balance += fee  # Mining reward
                    print(f"Rewarded {miner.name} with {fee} coins")
                    break
        else:
            print("Mining failed (timeout)")

        


    def validate_blockchain(self):
        valid = True
        n = len(self.blocks)-1
        i = 0
        while i < n:
            if self.blocks[i]['hash'] != self.blocks[i+1]['previous_hash']:
                valid = False
                break
            i += 1

        if valid:
            print('The blockchain is valid...')
        else:
            print('The blockchain is not valid...')

    def show_blockchain(self):
        for block in self.blocks:
            pprint(block)
            print()





def main():
    block_chain = Blockchain()
    print("Welcome to POW implementation")
    print("1. press 'n' to create a node")
    print("2. press 'm' to create a miner")
    print("3. press 't' to do a transaction")
    print("4. press 'e' to exit")
    print("5. press 'v' to validate blockchain")
    print("6. press 's' to show blockchain")
    print("7. type am to show all miners")
    print("8. type an to show all nodes")

    while True:
        command = input("\nEnter command: ").strip().lower()

        if command == 'n':  # Create new node
            while True:
                name = input("Enter node name: ").strip()
                if not name:
                    print("Name cannot be empty!")
                    continue

                if name in list(map(get_name, all_node)):
                    print("Error: Node with this name already exists")
                    continue

                try:
                    new_node = Node(name, block_chain)
                    print(f"New node '{name}' created with starting balance 1000")
                    print(f"Public key: {new_node.public_key.export_key().decode()}")
                    break
                except Exception as e:
                    print(f"Error creating node: {str(e)}")
                    break

        elif command == 'm':  # Create new miner
            while True:
                name = input("Enter miner name: ").strip()
                if not name:
                    print("Name cannot be empty!")
                    continue

                if name in list(map(get_name, all_node)):
                    print("Error: Name already exists as a node")
                    continue

                try:
                    new_miner = Miner(name, block_chain)
                    print(f"New miner '{name}' created with starting balance 1000")
                    print(f"Public key: {new_miner.public_key.export_key().decode()}")
                    break
                except Exception as e:
                    print(f"Error creating miner: {str(e)}")
                    break

        elif command == 't':  # Make transaction
            if not all_node:
                print("No nodes exist to make transactions")
                continue
                
            # Get sender
            sender_name = input("Enter sender name: ").strip()
            sender = next((n for n in all_node if n.name == sender_name), None)
            if not sender:
                print("Sender node not found")
                continue
                
            # Get recipient
            recipient_name = input("Enter recipient name: ").strip()
            if not recipient_name:
                print("Recipient name cannot be empty")
                continue
                
            # Get amount
            try:
                amount = float(input("Enter amount to send: ").strip())
                if amount <= 0:
                    print("Amount must be positive")
                    continue
            except ValueError:
                print("Invalid amount")
                continue
                
            # Get fee
            try:
                fee = float(input("Enter transaction fee: ").strip())
                if fee < 0:
                    print("Fee cannot be negative")
                    continue
            except ValueError:
                print("Invalid fee")
                continue
                
            # Check balance
            if sender.balance < amount + fee:
                print("Insufficient balance (amount + fee)")
                continue
                
            # Execute transaction
            try:
                sender.make_transaction(recipient_name, amount, fee)
                print("Transaction submitted for mining")
            except Exception as e:
                print(f"Transaction failed: {str(e)}")

        elif command == 'e':  # Exit
            print("Exiting blockchain system...")
            break

        elif command == 'v':  # Validate blockchain
            block_chain.validate_blockchain()

        elif command == 's':  # Show blockchain
            block_chain.show_blockchain()

        elif command == 'am':  # Show blockchain
            print(all_miners)

        elif command == 'an':  # Show blockchain
            print(all_node)
        else:
            print("Invalid command. Available commands:")
            print("n - Create new node")
            print("m - Create new miner")
            print("t - Make transaction")
            print("v - Validate blockchain")
            print("s - Show blockchain")
            print("am - Show all miners")
            print("an - Show all nodes")
            print("e - Exit")



main()