
from hashlib import sha256
from datetime import datetime
from Transaction import *

class Block:
    
    def __init__(self, block_hash, prev_block_hash, hash_of_transaction, time, nonce, block_transactions):
        # Header
        self.block_hash = block_hash
        self.prev_block_hash = prev_block_hash
        self.hash_of_transaction = hash_of_transaction
        self.time = time
        self.nonce = nonce
        # Contents
        self.block_transactions = block_transactions

        if self.block_hash == None:
            self.proof_of_work()


    @classmethod
    def create(cls, transaction_pool, prev_block_hash):
        transactions = transaction_pool.from_json_transactions()

        hash_of_transaction = sha256(str(transactions).encode('utf-8')).hexdigest()
        dtime = datetime.now()
        time = [dtime.year, dtime.month, dtime.day, dtime.hour, dtime.minute, dtime.second, dtime.microsecond]
        return cls(None, prev_block_hash, hash_of_transaction, time, 0, transactions)

    def proof_of_work(self):
        
        target = 6
        threshold = "0"*target

        found = False
        starttime = datetime.now()
        while found == False:
            toHash = str(self.to_json_header())
            hashed = sha256(toHash.encode('utf-8')).hexdigest()
            if hashed.startswith(threshold):
                endtime = datetime.now()
                found = True
                print (endtime - starttime)
                print (hashed)
                print (self.nonce)
            else:
                self.nonce += 1

        self.block_hash = hashed

    def to_json_header(self):
        return {
            'prev_block_hash': self.prev_block_hash,
            'hash_of_transaction': self.hash_of_transaction,
            'time': self.time,
            'nonce': self.nonce
        }

    def to_json_complete(self):
        return {
            'hash_pointer': self.block_hash,
            'header': self.to_json_header(),
            'transactions': self.block_transactions
        }

    @classmethod
    def from_json_compatible(cls, obj:dict):
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