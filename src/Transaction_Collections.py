
class Transaction_Unspent:

    def __init__(self, pub_key_str) -> None:
        
        self.pub_key_str = pub_key_str
        self.unspent = []
        self.my_unspent = []
        self.utxo = 0
    
    def add_my_unspent(self, transaction, value):
        if transaction not in self.my_unspent:
            self.my_unspent.append(transaction)
            self.utxo = self.utxo + value
            print('YOU JUST RECIEVED',value, 'SHMECKLES!!!')
    
    def add_unspent(self, transaction):
        if transaction not in self.unspent:
            self.unspent.append(transaction)

    def spent(self, transaction):
        for unspent in self.unspent:
            if unspent.to_json_complete == transaction.to_json_complete:

                if transaction in self.my_unspent:
                    self.my_unspent.remove(transaction)
                    self.utxo = self.utxo - transaction.outputs[0].value
                self.unspent.remove(transaction)




class Transaction_Pool:
    # not only holds the Transaction pool
    # also holds the unspent transactions from previos blocks
    
    def __init__(self, pub_key_str) -> None:
        self.list = [] # list of transaction objects
        self.pub_key_str = pub_key_str
        self.transactions_unspent = Transaction_Unspent(pub_key_str)
        self.fees = 0
    
    def add(self, transaction):
        if transaction in self.list:
            return False
        else:
            for i in range (len(transaction.outputs)): ########## BETTER
                if transaction.outputs[i].script_pub_key == self.pub_key_str:
                    self.transactions_unspent.add_my_unspent(transaction, transaction.outputs[i].value)
                    break
            self.transactions_unspent.add_unspent(transaction)
            self.list.append(transaction)
            return True
    
    def from_json_transactions(self):
        transactions = []
        for transaction in self.list:
            transactions.append(transaction)
        return transactions

    def to_json_complete(self):
        string = []
        for transaction in self.list:
            string.append(transaction.to_json_complete())
        return string
    
    def to_list_hash(self):
        transactions_hash = []
        for transaction in self.list:
            transactions_hash.append(transaction.hash)
        return transactions_hash
    
    def update_from_block(self, block):
        block_transactions = block.to_json_complete()['transactions']

        new_transaction_pool = []

        for pool_transaction in self.list:
            in_list = False
            for block_transaction in block_transactions:
                if block_transaction == pool_transaction.to_json_complete():
                    in_list = True
                    break
            if in_list == False:
                new_transaction_pool.append(pool_transaction)
        
        list_hash = self.to_list_hash()
        for block_transaction in block.block_transactions:
            if block_transaction.hash not in list_hash:
                if block_transaction.outputs[0].script_pub_key == self.pub_key_str:
                    self.transactions_unspent.add_my_unspent(block_transaction, block_transaction.outputs[0].value)
                self.transactions_unspent.add_unspent(block_transaction)
        
                if block_transaction.inputs[0].transaction_hash != 'COINBASE_TRANSACTION' or block_transaction.inputs[0].transaction_hash != 'GENERATED_HASH':
                    for t in self.transactions_unspent.unspent:
                            if t.get_hash() == block_transaction.inputs[0].transaction_hash:
                                self.transactions_unspent.spent(t)
                                break
        
        self.list = new_transaction_pool

                
