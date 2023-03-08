
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
            

    def add(self, block):
        self.blockchain.append(block)
        print(self.to_json_compatible())

    def head(self):
        return self.blockchain[-1]

    def prev_block_hash(self):
        prev_block = self.blockchain[-1]
        return prev_block.block_hash

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
