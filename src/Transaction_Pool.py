


class Transaction_Pool:
    # not only holds the Transaction pool
    # also holds the unspent transactions from previos blocks
    
    def __init__(self, pub_key_str) -> None:
        self.list = [] # list of transaction objects
        self.pub_key_str = pub_key_str
        self.list_json = []

    
    def add(self, transaction):
        if transaction.to_json_complete() in self.list_json:
            return False
        else:
            self.list.append(transaction)
            self.list_json.append(transaction.to_json_complete())
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
                double_spend = False
                for transaction in block.block_transactions:
                    # FOR DOUBLE SPEND
                    if transaction.inputs[0].transaction_hash == pool_transaction.inputs[0].transaction_hash and pool_transaction.type == 'MAIN':
                        print('Transaction moved from transaction pool because a double spend has been attempted', pool_transaction.to_json_complete())
                        double_spend = True
                        break
                if double_spend == False:
                    new_transaction_pool.append(pool_transaction)
        
        self.list = new_transaction_pool

                
