# Transaction

# import json
# # some JSON:
# x =  '{ "name":"John", "age":30, "city":"New York"}'

# # parse x:
# y = json.loads(x)

# # the result is a Python dictionary:
# print(y) 


from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class TransactionInput:
    
    hash_of_input: str
    index_of_inputs_prev_output_claimed: int
    scriptSig: str

@dataclass
class TransactionOutput:

    value: float
    scriptPubKey: str

class Transaction:

    def __init__(self, inputs: 'List[TransactionInput]', outputs: 'List[TransactionOutput]'):
        self.inputs = inputs
        self.outputs = outputs

        # Labchain put this in the header
        self.timestamp = datetime.now() # lockTime in book?
        # VI - labchain

        self.num_inputs = len(self.inputs)
        self.num_outputs = len(self.outputs)

        # to be made a function of later
        self.hash = None

        # IN BOOK self.size

        # EXTRA: self.transaction = sum of inputs - sum of outputs

