from block import Block
import random

class Node:
    def __init__(self,name,balance):
        self.id=random.randint(0,1000)
        self.name=name
        self.balance=balance
        self.blockchain=[]        

    # Function for updating the copy of the blockchain
    def updateBlockchain(self,block):
        self.blockchain.append(block)

    # Function for returning the current balance
    def checkBalance(self):
        return str(self.balance) + " BKC"