import hashlib


def mine_block(block, difficulty=3):
    target = "0" * difficulty
    while True:
        hash_data = f"{block.prev_hash}{block.name}{block.data}{block.nonce}"
        computed_hash = compute_hash(hash_data)
        if computed_hash.startswith(target):
            block.hash = computed_hash
            block.miner = True
            break
        block.nonce += 1
        
class Block:
    def __init__(self, name, data,new_hash,  prev_hash, is_miner = False,nonce = 0):
        self.name = name
        self.data = data
        self.hash = new_hash
        self.prev_hash = prev_hash
        self.miner = is_miner
        self.nonce = nonce
        
        
def compute_hash(hash_data):
    hash_object = hashlib.sha1(hash_data.encode())
    hash_value = hash_object.hexdigest()
    return hash_value

def main():
    prev_hash = "0" *64
    difficulty = 3
    
    Blockchain = []
    num = int(input("Enter the number of Nodes you want to Add"))
    for i in range(0,num):
        name = input("Enter Your Name: ")
        data = int(input("Enter the Data: "))
    
    
        block = Block(name,data, "", prev_hash)
        mine_block(block, difficulty)

        prev_hash = block.hash
        
        Blockchain.append(block)
        
        
    for i, block in enumerate(Blockchain):
        print(block.name)
        print(block.data)
        print(block.hash)
        print(block.prev_hash)
        print("\n")

if __name__=='__main__':
    main()
        
        
        