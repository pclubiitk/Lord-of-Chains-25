from block import Block
from node import Node
import hashlib
import random

# Extended Euclidean Algorithm to find modular inverse
def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

# Function to compute modular inverse of a with respect to modulus m
def modinv(a, m):
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception("Modular inverse doesn't exist")
    return x % m

# Function to sign a message using RSA private key
def sign(message, privkey, n):
    hash_value = int(hashlib.sha256(message.encode()).hexdigest(), 16)
    hash_value = hash_value % n
    return pow(hash_value, privkey, n)

# Function to verify a digital signature using RSA public key
def verify(message, signature, pubkey, n):
    hash_value = int(hashlib.sha256(message.encode()).hexdigest(), 16)
    hash_value = hash_value % n
    decrypted_hash = pow(signature, pubkey, n)
    return hash_value == decrypted_hash

# User inputs name and initial balance, a node is created for them
name = input("Hello! Please enter your name to begin \n")
balance = int(input("Enter your initial balance \n"))
user_node = Node(name, balance)
print("Your node with id", user_node.id, "has been initialised")

# Create a list of nodes including the user and 4 random nodes
nodes = [user_node]
for i in range(1, 5):
    n = Node("Random", random.randint(0, 500))
    nodes.append(n)
    print("Random node with id", n.id, "has been initialised")

# RSA key generation setup using two user-input primes
p = int(input("Enter first prime (>10) for key generation: "))
q = int(input("Enter second prime (>10): "))
n = p * q
e_totient = (p - 1) * (q - 1)
pubkey = 17
privkey = modinv(pubkey, e_totient)
print("Public Key:", pubkey, ", Private Key:", privkey)

# Blockchain initialization with a genesis block
blocks = []
origin = Block(0, [0], "0")
blocks.append(origin)

# Avalanche consensus parameters
quorum = 20
majority = round(0.7 * quorum)
threshold = 5

# Initialize transaction list and block counter
tr_list = []
tr_counter = 1

# Main interaction loop
while True:
    print("\nWelcome to Bakchod Blockchain!")
    print("1 - Make transactions")
    print("2 - Check node balances")
    print("3 - Exit")

    choice = int(input("Enter your choice: "))

    if choice == 1:
        # Allow user to enter up to 3 transactions per round
        for i in range(3):
            message = input("Enter amount for transaction (0 to stop): ")

            if message == "0":
                break

            amount = int(message)

            if amount > user_node.balance:
                print(" Not enough balance.")
                break

            # Sign and verify the transaction
            signature = sign(message, privkey, n)
            print("Digital Signature:", signature)
            is_valid = verify(message, signature, pubkey, n)
            print("Signature valid?", is_valid)

            if not is_valid:
                print(" Invalid signature.")
                break

            # Begin Avalanche-style consensus simulation
            consec = 0
            old_pref = None
            decision = False
            check_count = 0

            while not decision:
                # Simulate a round of random binary votes (0 or 1)
                votes = [random.randint(0, 1) for _ in range(quorum)]
                pref = votes.count(1) >= majority

                # Check if this round's preference is consistent with previous rounds
                if pref == old_pref or check_count == 0:
                    consec += 1
                else:
                    consec = 1
                old_pref = pref

                # If we reach enough consistent rounds, finalize decision
                if consec >= threshold:
                    decision = True

                check_count += 1

            if decision:
                receiver_id = int(input("Enter recipient node ID: "))
                receiver = next((n for n in nodes if n.id == receiver_id), None)

                if receiver:
                    user_node.balance -= amount
                    receiver.balance += amount
                    tr_list.append(f"{user_node.id}->{receiver.id}:{amount}")
                    print("Transaction confirmed via Avalanche Consensus!")
                else:
                    print("Invalid recipient ID.")

        # If any transactions were confirmed, create and add a new block
        if tr_list:
            block = Block(tr_counter, tr_list, blocks[-1].hash)
            blocks.append(block)

            # Update each node's local blockchain
            for node in nodes:
                node.blockchain.append(block)

            print("Block Added")
            tr_list.clear()
            tr_counter += 1

    elif choice == 2:
        # Print current balance of all nodes
        for node in nodes:
            print("Node", node.id, "balance:", node.checkBalance())

    elif choice == 3:
        # Exit the program
        break

    else:
        print("Invalid choice.")
