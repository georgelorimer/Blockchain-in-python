
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

        self.target = 5
        self.threshold = "0"*self.target

        if self.block_hash == None:
            self.proof_of_work()

    @classmethod
    def create(cls, transaction_pool, prev_block_hash, creator):

        transactions = transaction_pool.from_json_transactions()
        fee = 0
        for transaction in transactions:
            if transaction.type == 'FEE':
                fee += transaction.outputs[0].value
        t = Transaction(None,[Transaction_Input("COINBASE_TRANSACTION", 'None')], [Transaction_Output('P2PK:' + creator, 50+fee)], datetime.now(), 'COINBASE')
        transactions.insert(0, t)

        hash_of_transaction = sha256(str(transactions).encode('utf-8')).hexdigest()

        dtime = datetime.now()
        time = [dtime.year, dtime.month, dtime.day, dtime.hour, dtime.minute, dtime.second, dtime.microsecond]

        return cls(None, prev_block_hash, hash_of_transaction, time, 0, transactions)

    def proof_of_work(self):
        
        
        found = False
        starttime = datetime.now()
        
        while found == False:
            toHash = str(self.to_json_header())
            hashed = sha256(toHash.encode('utf-8')).hexdigest()
            if hashed.startswith(self.threshold):
                endtime = datetime.now()
                found = True
                print (endtime - starttime)
                print (hashed)
                print (self.nonce)
            else:
                self.nonce += 1

        self.block_hash = hashed

    # def verify

    def to_json_header(self):
        return {
            'prev_block_hash': self.prev_block_hash,
            'hash_of_transaction': self.hash_of_transaction,
            'time': self.time,
            'nonce': self.nonce
        }

    def to_json_complete(self):
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
        text = self.txt_format()
        file = open('text/block_file.txt', 'w')
        file.write(text)
        file.close()
        os.system('open -t text/block_file.txt')
        
