


class Transaction_Pool:
    """Transaction_Pool holds all the transactions in the current round to be made into a new block

    :ivar list: list of all the transactions in the pool
    :vartype list: list of Transaction
    :ivar pub_key_str: sting of public key
    :vartype pub_key_str: str
    :ivar list_json: list of json representations of transactions
    :vartype list_json: list of json

    """
    
    def __init__(self, pub_key_str) -> None:
        """_summary_

        Args:
            pub_key_str (str): string of public key
        """
        self.list = []
        self.pub_key_str = pub_key_str
        self.list_json = []

    
    def add(self, transaction):
        """Adds transaction if transaction is not already present

        Args:
            transaction (Transaction): transaction to add

        Returns:
            bool: was transaction added
        """
        if transaction.to_json_complete() in self.list_json:
            return False
        else:
            self.list.append(transaction)
            self.list_json.append(transaction.to_json_complete())
            return True
    
    def list_of_transactions(self):
        """returns list of transactions

        Returns:
            list: list of transactions
        """
        transactions = []
        for transaction in self.list.copy():
            transactions.append(transaction)
        return transactions

    def to_json_complete(self):
        """to json representation

        Returns:
            list: of json transactions 
        """
        string = []
        for transaction in self.list:
            string.append(transaction.to_json_complete())
        return string
    
    def to_list_hash(self):
        """list of transaction hashes

        Returns:
            list: of transaction hashes
        """
        transactions_hash = []
        for transaction in self.list.copy():
            transactions_hash.append(transaction.hash)
        return transactions_hash
    
    def update_from_block(self, block):
        """When a new block is created, the transaction pool will be updated.
        All transactions that have not been added to the blockchain will remain.
        Any double spends will be found here

        Args:
            block (Block): block to update from
        """
        block_transactions = block.to_json_complete()['transactions']

        new_transaction_pool = []

        for pool_transaction in self.list.copy():
            in_list = False
            for block_transaction in block_transactions:
                if block_transaction == pool_transaction.to_json_complete():
                    in_list = True
                    break
            if in_list == False:
                double_spend = False
                for transaction in block.block_transactions:
                    for input_transaction in transaction.inputs:
                        for input_pool in pool_transaction.inputs:

                            if transaction.inputs[0].transaction_hash == pool_transaction.inputs[0].transaction_hash and pool_transaction.type == 'MAIN':
                                double_spend = True
                                break
                        if double_spend == True:
                            break
                    if double_spend == True:
                        break
                if double_spend == False:
                    new_transaction_pool.append(pool_transaction)
        
        self.list = new_transaction_pool

                
