import hashlib

class Block:
    def __init__(self,index,transaction_list,prevhash,nonce=0):
        self.index=index
        self.transaction_list=transaction_list
        self.prevhash=prevhash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    # Function for calculating the hash of the current block
    def calculate_hash(self):
        data = str(self.index) + self.prevhash + str(self.calcTransactionString()) + str(self.nonce)
        return hashlib.sha256(data.encode()).hexdigest()
    
    # Function for generating the concatenated string of transactions 
    def calcTransactionString(self):
        transactions_str = '-'.join(str(tx) for tx in self.transaction_list) 
        return transactions_str

