
# class Transaction_Unspent:

# class Transactions_for_Block

class Transaction_Pool:
    # not only holds the Transaction pool
    # also holds the unspent transactions from previos blocks
    
    def __init__(self) -> None:
        self.list = [] # list of transaction objects
    
    def add(self, transaction):
        if transaction in self.list:
            return False
        else:
            ############# CHECK FOR VALIDITY #############
            self.list.append(transaction)
            return True



