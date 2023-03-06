
from Block import *

from datetime import datetime

# change datetime
GENESIS_BLOCK = Block("GENESIS_HASH", None, None, datetime(2023, 3, 6, 12, 32, 45, 753237), 0, [])

class Blockchain:
    def __init__(self, blockchain) -> None:
        if blockchain != None:
            self.blockchain = blockchain
        else:
            self.blockchain = [GENESIS_BLOCK]

    def add(self, block):
        self.blockchain.append(block)

    def head(self):
        return self.list[-1].to_json_complete()

    def prev_block_hash(self):
        prev_block = self.list[-1].to_json_complete()
        return prev_block['hash_pointer']

    def 

