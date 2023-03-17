from dataclasses import dataclass
from typing import List
from datetime import datetime
from collections import namedtuple
from hashlib import sha256


from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa
import base58

class Transaction_Input(namedtuple("Transaction_Input", ["transaction_hash", "output_id", "script_sig"])):

    @classmethod
    def from_json_compatible(cls, obj):
        """ Creates a new object of this class, from a JSON-serializable representation. """
        return cls(str(obj['transaction_hash']), int(obj['output_id']), obj['script_sig'])

    def to_json_compatible(self):
        """ Returns a JSON-serializable representation of this object. """
        return {
            'transaction_hash': self.transaction_hash,
            'output_id': self.output_id,
            'script_sig': self.script_sig
        }


class Transaction_Output(namedtuple("Transaction_Output", ["script_pub_key", "value"])):

    @classmethod
    def from_json_compatible(cls, obj):
        """ Creates a new object of this class, from a JSON-serializable representation. """
        return cls(str(obj['script_pub_key']), int(obj['value']))

    def to_json_compatible(self):
        """ Returns a JSON-serializable representation of this object. """
        return {
            'script_pub_key': self.script_pub_key,
            'value': self.value
        }

    
class Transaction:

    def __init__(self, hash: str, inputs: 'List[Transaction_Input]', outputs: 'List[Transaction_Output]', timestamp: 'datetime', type: str):
        self.inputs = inputs
        self.outputs = outputs
        self.timestamp = timestamp
        self.hash = hash
        if self.hash == None:
            self.hash = self.get_hash()
        self.type = type

    def get_hash(self):
        if self.hash == None:
            to_hash = str(self.to_json_contents())
            self.hash = sha256(to_hash.encode('utf-8')).hexdigest()
        return self.hash
        

    def to_json_contents(self):
        """ Returns a JSON-serializable representation of this object. """
        val = {}
        val['inputs'] = []
        for inp in self.inputs:
            val['inputs'].append(inp.to_json_compatible())
        val['outputs'] = []
        for out in self.outputs:
            val['outputs'].append(out.to_json_compatible())
        val['timestamp'] = self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f UTC")
        return val

    def to_json_complete(self):
        return {
            "hash_pointer" : self.get_hash(),
            "contents" : self.to_json_contents(),
            'type' : self.type
        }

    @classmethod
    def from_json_compatible(cls, obj: dict):
        """ Creates a new object of this class, from a JSON-serializable representation. """
        hashp = obj['hash_pointer']

        t_type = obj['type']

        content = obj['contents']

        inputs = []
        for inp in content['inputs']:
            inputs.append(Transaction_Input.from_json_compatible(inp))
        outputs = []
        for out in content['outputs']:
            outputs.append(Transaction_Output.from_json_compatible(out))
        timestamp = datetime.strptime(content['timestamp'], "%Y-%m-%dT%H:%M:%S.%f UTC")
        return cls(hashp, inputs, outputs, timestamp, t_type)

    def verify(self, input_transaction, unspent):
        verified_unspent = self.verify_unspent(input_transaction, unspent)
        if verified_unspent == False:
            return False

        # Get key from the output
        inp_script_pub_key = input_transaction.outputs[0].script_pub_key
        inp_key_array = inp_script_pub_key.split(':')

        if inp_key_array[0] == "P2PK":
            input_key = inp_key_array[1]

        elif inp_key_array[0] == "P2PKS":
            if self.check_addr(inp_key_array[1]) == False:
                print('Secure key not valid')
                return False
            input_key = self.addr_to_pub(inp_key_array[1])
        else:
            return False
        

        # Verify signature
        input_key_split = input_key.split('+')
        pub = ECC.construct(curve='ed25519', point_x = int(input_key_split[0]), point_y = int(input_key_split[1]))

        signature = self.inputs[0].script_sig

        message = str(input_transaction.to_json_complete()).encode('utf-8')

        verifier = eddsa.new(pub, 'rfc8032')
        try:
            verifier.verify(message, signature)
            print("The message is authentic")
            return True
        except ValueError:
            print("The message is not authentic")
            return False

        # ammounts for from transaction
    def verify_unspent(self, input_transaction, unspent):
        if self.type == 'MAIN':
            if input_transaction not in unspent:
                print('This transaction is already spent')
                return False
            else:
                print('This transaction has not yet been spent')
                return True

    def check_addr(self, addr):
        addr_split= addr.split('+')

        check_string = addr_split[0] + '+' + addr_split[1] + '+'

        check_cs = sha256(check_string.encode('utf-8')).hexdigest()[:8]

        if check_cs == addr_split[2]:
            return True
        else:
            return False
    
    def addr_to_pub(self, addr):
        addr_array = addr.split('+')
        bytex = base58.b58decode(addr_array[0].encode('utf-8'))
        bytey = base58.b58decode(addr_array[1].encode('utf-8'))

        x= int.from_bytes(bytex, 'big')
        y= int.from_bytes(bytey, 'big')

        pub_key_str = str(x) + "+" +str(y)

        return pub_key_str
