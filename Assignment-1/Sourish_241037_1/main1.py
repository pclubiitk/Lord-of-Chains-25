from block import Block
from miner import Miner
from node import Node
from block import Block
import hashlib
import random

def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def modinv(a, m):
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception("Modular inverse doesn't exist")
    return x % m

def sign(message, privkey, n):
    hash_value = int(hashlib.sha256(message.encode()).hexdigest(), 16)
    hash_value = hash_value % n
    return pow(hash_value, privkey, n)

def verify(message, signature: int, pubkey, n):
    hash_value = int(hashlib.sha256(message.encode()).hexdigest(), 16)
    hash_value = hash_value % n
    decrypted_hash = pow(signature, pubkey, n)
    return hash_value == decrypted_hash

# Initializng nodes
name=input("Hello! Please enter your name to begin \n")
balance=int(input("Enter your initial balance \n"))
node=Node(name,balance)
print("Your node with id ",node.id," has been initialised")

nodes=list()
nodes.append(node)

for i in range(1,5):
    nodes.append(Node(" ",random.randint(0,500)))
    print("A random node with id ",nodes[i].id," has been initialised")

# Taking user input for primes to generate public and private keys 
p = int(input("Please enter the first generating prime (greater than 10) for your keys "))
q = int(input("Please enter the second generating prime (greater than 10) for your keys "))

# Computing n and Euler's Totient and implementing the RSA algorithm
n = p * q  
e_totient = (p - 1) * (q - 1) 

# Generating the key pair
pubkey = 17
privkey = modinv(pubkey, e_totient)
print("Private Key: ", privkey)
print("Public Key: ", pubkey)
 
# Creating list of blocks and adding origin block to the list 
blocks=list()
origin=Block(0,[0],"0")
blocks.append(origin)

# Creating list of miners to mine blocks 
minerlist=list()
for i in range(5):
    miner=Miner(random.randint(1,6))
    minerlist.append(miner)

#Taking multiple transactions in 1 or more than 1 blocks, signing and verifying them too 
tr_list=list()
tr_counter=0

choice=0

while(True):
    print("Welcome to Bakchod Blockchain! Press 1 to initiate/continue transactions Press 2 to check node and miner balances, Press 3 to exit ")
    choice = int(input("Enter your choice "))

    if(choice==1):
        for i in range(3):
            message = input("Please enter your amount for the transaction. You can enter upto 3 transactions for a single block. Press 0 to stop ")

            if(message=="0"):
                break

            if((int)(message)>node.balance):
                print("Sorry, you do not have the money to make this transaction")
                break

            # Signing and verifying using public and private keys 
            signature = sign(message, privkey, n)
            print("Digital Signature: ", signature)

            is_valid = verify(message, signature, pubkey, n)
            print("Signature valid? ", is_valid)

            node.balance-=(int)(message)

            receiver=int(input("Enter the ID of the node to which you want to sent the transaction "))
            for recipient_node in nodes:
                if recipient_node.id==receiver:
                    recipient_node.balance+=(int)(message)

            tr_list.append(message)
            print("Transaction recorded")

        tr_counter+=1

        # Creating blocks and adding them to a temporary list 
        block=Block(tr_counter,tr_list,blocks[tr_counter-1].hash)
        blocks.append(block)

        tr_list.clear()

        # Mining block
        miner_index=random.randint(0,5)
        minerlist[miner_index].mineBlock(block)
        print("Miner ",miner_index," mined your block!")

        # Updating each node with the mined block
        for i in range(5):
            nodes[i].blockchain.append(block)

    # Displaying balances of nodes and miners
    if(choice == 2):
        for i in range(5):
            print("Balance of Node ", nodes[i].id," is ",nodes[i].checkBalance())
        
        for i in range(5):
            print("Balance of Miner ", minerlist[i].id," is ",minerlist[i].checkBalance())

    if(choice==3):
        break