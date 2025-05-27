from block import Block
import random

class Miner:
    def __init__(self,id,balance=0):
        self.balance=balance
        self.id=random.randint(0,1000)
    
    # Function for mining a block with PoW consensus mechanism
    def mineBlock(self,block,difficulty=5):
        while not block.hash.startswith('0' * difficulty):
            block.nonce += 1
            block.hash = block.calculate_hash()
        print("Block has been mined! The nonce is ",block.nonce)
        self.balance+=25

    # Function for returning the current balance
    def checkBalance(self):
        return str(self.balance) + " BKC"





