
from hashlib import sha256
from datetime import datetime
from Transaction import *
import subprocess, os, platform

class Block:
    """Block contains all the attributes of a block

    :ivar block_hash: The hash of the entire block.
    :vartype block_hash: str
    :ivar prev_block_hash: The hash of the last block.
    :vartype prev_block_hash: str
    :ivar hash_of_transaction: The hash of the transactions.
    :vartype hash_of_transaction: str
    :ivar time: The time stamp of the block, when it was made.
    :vartype time: list of int
    :ivar nonce: The number that when hashed with the block, the block_hash is below the threshold.
    :vartype nonce: int
    :ivar block_transactions: The list of all the transactions of the block.
    :vartype block_transactions: list of Transaction
    :ivar target: The size of the threshold.
    :vartype target: int
    :ivar threshold: The amount of 0s a block hash needs to start with.
    :vartype threshold: str

    """

    
    def __init__(self, block_hash, prev_block_hash, hash_of_transaction, time, nonce, block_transactions):
        """innit

        Args:
            block_hash (str): The hash of the entire block.
            prev_block_hash (str): The hash of the last block.
            hash_of_transaction (str): The hash of the transactions.
            time (list of int): The time stamp of the block, when it was made.
            nonce (int): The number that when hashed with the block, the block_hash is below the threshold.
            block_transactions (list of Transaction): The list of all the transactions of the block.
        """
        # Header
        self.block_hash = block_hash
        self.prev_block_hash = prev_block_hash
        self.hash_of_transaction = hash_of_transaction
        self.time = time
        self.nonce = nonce
        # Contents
        self.block_transactions = block_transactions

        self.target = 5
        self.threshold = "0"*self.target

        if self.block_hash == None:
            self.proof_of_work()

    @classmethod
    def create(cls, transaction_pool, prev_block_hash, creator):
        """Returns a block object.

        Args:
            transaction_pool (Transaction_Pool): copy of the transaction pool
            prev_block_hash (str): hash of the previos block
            creator (str): pub_key_string of the creator of the block

        Returns:
            Block: Block object
        """

        transactions = transaction_pool.list_of_transactions()
        fee = 0
        for transaction in transactions:
            if transaction.type == 'FEE':
                fee += transaction.outputs[0].value
        t = Transaction(None,[Transaction_Input("COINBASE_TRANSACTION", 'None')], [Transaction_Output('P2PK:' + creator, 50+fee)], datetime.now(), 'COINBASE')
        transactions.insert(0, t)

        json_transactions = []
        for transaction in transactions:
            json_transactions.append(transaction.to_json_complete())

        hash_of_transaction = sha256(str(json_transactions).encode('utf-8')).hexdigest()

        dtime = datetime.now()
        time = [dtime.year, dtime.month, dtime.day, dtime.hour, dtime.minute, dtime.second, dtime.microsecond]

        return cls(None, prev_block_hash, hash_of_transaction, time, 0, transactions)

    def proof_of_work(self):
        """Creates the hash by incrementing the nonce, hashing the block and checking if it meets the threshold requirements
        """
        
        found = False
        
        while found == False:
            toHash = str(self.to_json_header())
            hashed = sha256(toHash.encode('utf-8')).hexdigest()
            if hashed.startswith(self.threshold):
                found = True
            else:
                self.nonce += 1

        self.block_hash = hashed

    def to_json_header(self):
        """Returns a json representation of the header

        Returns:
            dict: Json representation of the header
        """
        return {
            'prev_block_hash': self.prev_block_hash,
            'hash_of_transaction': self.hash_of_transaction,
            'time': self.time,
            'nonce': self.nonce
        }

    def to_json_complete(self):
        """Returns a json representation of the entire block

        Returns:
            dict: json representation of the entire block
        """
        transactions = []
        for transaction in self.block_transactions:
            transactions.append(transaction.to_json_complete())
        return {
            'hash_pointer': self.block_hash,
            'header': self.to_json_header(),
            'transactions': transactions
        }

    @classmethod
    def from_json_compatible(cls, obj:dict):
        """Turns json representation into an object

        Args:
            obj (dict): json representation of a block

        Returns:
            Block: object
        """
        block_hash = obj['hash_pointer']
        header = obj['header']
        prev_block_hash = header['prev_block_hash']
        hash_of_transaction = header['hash_of_transaction']
        time = header['time']
        nonce = header['nonce']
        block_transactions_str = obj['transactions']

        block_transactions = []
        for transaction in block_transactions_str:
            block_transactions.append(Transaction.from_json_compatible(transaction))

        return cls(block_hash, prev_block_hash, hash_of_transaction, time, nonce, block_transactions)
    
    def txt_format(self):
        """Returns block into a .txt format

        Returns:
            str: block.txt
        """
        winner = self.block_transactions[0].outputs[0].script_pub_key.split(':')
        pk = winner[1]
        h_text = 'Block Explorer\n' + 'Header:\n\tHash: '+self.block_hash+'\n\tHash of previos block: '+self.prev_block_hash+'\n\tHash of Transactions: '+self.hash_of_transaction+'\n\tTime Stamp: '+str(self.time)+'\n\tNonce: '+str(self.nonce)+'\n\tBlock Reward: 50\n\tTransaction Fee: '+str(self.block_transactions[0].outputs[0].value - 50)+'\n\tBlock creator: '+pk
        b_text = h_text + '\n------------------------------------------------------------------------------\n------------------------------------------------------------------------------\nContents:'
        for i in range(len(self.block_transactions)):
            b_text = b_text+'\n------------------------------------------------------------------------------\n'
            b_text = b_text + 'Transaction '+ str(i+1)+ ': \n'
            b_text = b_text + self.block_transactions[i].txt_format()
        
        return b_text
        
    def to_txt(self):
        """Creates the file: block_file.txt and opens it
        """
        text = self.txt_format()
        file = open('text/block_file.txt', 'w')
        file.write(text)
        file.close()
        
        filepath = 'text/block_file.txt'
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(filepath)
        else:                                   # linux variants
            subprocess.call(('xdg-open', filepath))
