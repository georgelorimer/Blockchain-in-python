
from Block import *

from datetime import datetime
from hashlib import sha256


time = datetime.now()
GENESIS_TIME = [time.year, time.month, time.day, time.hour, time.minute, time.second, time.microsecond]
GENESIS_BLOCK = Block("GENESIS_HASH", None, None, GENESIS_TIME, 0, [])

class Blockchain:
    """Blockchain class is holds the personal blockchain of each node
    
    :ivar blockchain: List of the entire block.
    :vartype blockchain: list of Block
    """
    
    def __init__(self, blockchain) -> None:
        """innit

        Args:
            blockchain (list of Block): list of blocks
        """
        if blockchain == None:
            self.blockchain = [GENESIS_BLOCK]
        else:
            self.blockchain = blockchain
    
    ### UTILITY FUNCTIONS ###
    def add(self, block):
        """Verifies prev_block_hash, hash_transaction and nonce, then adds the block.

        Args:
            block (object Block): block object

        Returns:
            bool: True if block is correct and has been added, False otherwise
        """
        if self.blockchain[-1].block_hash != block.prev_block_hash:
            print('Invalid Block')
            return False
        else:

            toHash = str(block.to_json_header())
            hashed = sha256(toHash.encode('utf-8')).hexdigest()

            if hashed.startswith(block.threshold) == False:
                print('Nonce is incorrect')
                return False
        
        json_transactions = []
        for transaction in block.block_transactions:
            json_transactions.append(transaction.to_json_complete())

        if block.hash_of_transaction != sha256(str(json_transactions).encode('utf-8')).hexdigest():
            print('Transaction hash not valid')
            return False

        self.blockchain.append(block)
        return True


    def head(self):
        """returns the head of the block

        Returns:
            Block: last block
        """
        return self.blockchain[-1]

    def prev_block_hash(self):
        prev_block = self.blockchain[-1]
        return prev_block.block_hash


    ### JSON FUNCTIONS ###
    def to_json_compatible(self):
        """Returns json representation of blockchain

        Returns:
            dict: json representation of blockchain
        """
        blockchain = []
        for block in self.blockchain:
            blockchain.append(block.to_json_complete())
        return {
            'blockchain': blockchain
            }
    @classmethod
    def from_json_compatible(cls, obj: dict):
        """Creates blockchain from json representation

        Args:
            obj (dict): json representation of blockchain

        Returns:
            Blockchain: Blockchain
        """
        new_blockchain = []
        for block in obj['blockchain']:
            new_blockchain.append(Block.from_json_compatible(block))
        return cls(new_blockchain)


    def return_transactions(self):
        """Returns all the transactions in the blockchain apart from the genesis block

        Returns:
            list of Transaction: all the transactions
        """
        blockchain_transactions = []

        for i in range(1, len(self.blockchain)):
            block = self.blockchain[i]

            for transaction in block.block_transactions:
                blockchain_transactions.append(transaction)

        return blockchain_transactions