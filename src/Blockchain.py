
from Block import *

from datetime import datetime

# change datetime
time = datetime.now()
GENESIS_TIME = [time.year, time.month, time.day, time.hour, time.minute, time.second, time.microsecond]
GENESIS_BLOCK = Block("GENESIS_HASH", None, None, GENESIS_TIME, 0, [])

class Blockchain:
    def __init__(self, blockchain) -> None:
        if blockchain == None:
            self.blockchain = [GENESIS_BLOCK]
        else:
            self.blockchain = blockchain
    
    ### UTILITY FUNCTIONS ###
    def add(self, block):
        if self.blockchain[-1].block_hash != block.prev_block_hash:
            print('Invalid Block')
            return False
        else:

            toHash = str(block.to_json_header())
            hashed = sha256(toHash.encode('utf-8')).hexdigest()

            if hashed.startswith(block.threshold):
                self.blockchain.append(block)
                return True
            else:
                print('Nonce is incorrect')
                return False

    def head(self):
        return self.blockchain[-1]

    def prev_block_hash(self):
        prev_block = self.blockchain[-1]
        return prev_block.block_hash


    ### JSON FUNCTIONS ###
    def to_json_compatible(self):
        blockchain = []
        for block in self.blockchain:
            blockchain.append(block.to_json_complete())
        return {
            'blockchain': blockchain
            }
    @classmethod
    def from_json_compatible(cls, obj: dict):
        new_blockchain = []
        for block in obj['blockchain']:
            new_blockchain.append(Block.from_json_compatible(block))
        return cls(new_blockchain)


    def return_transactions(self):
        blockchain_transactions = []

        for i in range(1, len(self.blockchain)):
            block = self.blockchain[i]

            for transaction in block.block_transactions:
                blockchain_transactions.append(transaction)

        return blockchain_transactions