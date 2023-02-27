from dataclasses import dataclass
from typing import List
from datetime import datetime
from collections import namedtuple
from hashlib import sha256


class Transaction_Input(namedtuple("Transaction_Input", ["transaction_hash", "output_id", "script_sig"])):

    @classmethod
    def from_json_compatible(cls, obj):
        """ Creates a new object of this class, from a JSON-serializable representation. """
        return cls(str(obj['transaction_hash']), int(obj['output_id']), str(obj['script_sig']))

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

    def __init__(self, hash: str, inputs: 'List[Transaction_Input]', outputs: 'List[Transaction_Output]', timestamp: 'datetime'):
        self.inputs = inputs
        self.outputs = outputs
        self.timestamp = timestamp
        self.hash = hash
        if self.hash == None:
            self.hash = self.get_hash()

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
            "contents" : self.to_json_contents()
        }

    @classmethod
    def from_json_compatible(cls, obj: dict):
        """ Creates a new object of this class, from a JSON-serializable representation. """
        hashp = obj['hash_pointer']

        content = obj['contents']

        inputs = []
        for inp in content['inputs']:
            inputs.append(Transaction_Input.from_json_compatible(inp))
        outputs = []
        for out in content['outputs']:
            outputs.append(Transaction_Output.from_json_compatible(out))
        timestamp = datetime.strptime(content['timestamp'], "%Y-%m-%dT%H:%M:%S.%f UTC")
        return cls(hashp, inputs, outputs, timestamp)

    def verify(self):
        # Signing
        # ammounts
        
