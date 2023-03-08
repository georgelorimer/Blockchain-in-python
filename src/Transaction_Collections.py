
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

    # def update <--- updates from transaction pool adn blockchain
    
    # def utxo
        # work out transaction
        # return self.utxo

    # COME BACK TO THIS
    # def utxo(self):
    #     balance = 0
    #     for transaction in self.my_unspent:
    #         for output in transaction.outputs:
    #             if output.script_pub_key == self.pub_key_str:
    #                 out



class Transaction_Pool:
    # not only holds the Transaction pool
    # also holds the unspent transactions from previos blocks
    
    def __init__(self, pub_key_str) -> None:
        self.list = [] # list of transaction objects
        self.pub_key_str = pub_key_str
        self.transactions_unspent = Transaction_Unspent(pub_key_str)
    
    def add(self, transaction):
        if transaction in self.list:
            return False
        else:
            ############# CHECK FOR VALIDITY #############
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
            transactions.append(transaction.to_json_complete())
        return transactions
    
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
        
        self.list = new_transaction_pool
        # self.transactions_unspent.update(block)
                
