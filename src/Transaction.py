from dataclasses import dataclass
from typing import List
from datetime import datetime
from collections import namedtuple
from hashlib import sha256
import subprocess, os, platform


from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa
import base58

class Transaction_Input(namedtuple("Transaction_Input", ["transaction_hash", "script_sig"])):
    """Transaction inputs

    Args:
        namedtuple (list): transaction_hash- hash of the transaction to spend, script_sig- signature of input
    """

    @classmethod
    def from_json_compatible(cls, obj):
        """ Creates a new object of this class, from a JSON-serializable representation. """
        return cls(str(obj['transaction_hash']), obj['script_sig'])

    def to_json_compatible(self):
        """ Returns a JSON-serializable representation of this object. """
        return {
            'transaction_hash': self.transaction_hash,
            'script_sig': self.script_sig
        }
    def to_txt_format(self):
        """Returns .txt format of input

        Returns:
            str: returns input in txt format
        """
        return '\tInput Hash: '+ self.transaction_hash+'\n\tScript Signature: '+ str(self.script_sig)


class Transaction_Output(namedtuple("Transaction_Output", ["script_pub_key", "value"])):
    """Transaction inputs

    Args:
        namedtuple (list): script_pub_key- script choice + key/address, value- value of the output
    """

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
    
    def to_txt_format(self):
        """Returns .txt format of output

        Returns:
            str: returns output in txt format
        """
        return '\n\tScript Pub Key: '+ self.script_pub_key+'\n\tValue: '+ str(self.value)

    
class Transaction:
    """Transaction holds the attributes of a transaction

    :ivar inputs: list of inputs
    :vartype inputs: list of Transaction_Input
    :ivar outputs: list of outputs
    :vartype outputs: list of Transaction_Outputs
    :ivar timestamp: time stamp of transaction
    :vartype timestamp: datetime
    :ivar hash: hash of transaction
    :vartype hash: str
    :ivar type: transaction type - MAIN, CHANGE, FEE, COINBASE, GEN
    :vartype type: str

    """

    def __init__(self, hash: str, inputs: 'List[Transaction_Input]', outputs: 'List[Transaction_Output]', timestamp: 'datetime', type: str):
        """innit

        Args:
            hash (str): hash of transaction
            inputs (List[Transaction_Input]): list of inputs
            outputs (List[Transaction_Output]): list of outputs
            timestamp (datetime): time stamp of transaction
            type (str): transaction type - MAIN, CHANGE, FEE, COINBASE, GEN
        """
        self.inputs = inputs
        self.outputs = outputs
        self.timestamp = timestamp
        self.hash = hash
        if self.hash == None:
            self.hash = self.get_hash()
        self.type = type

    def get_hash(self):
        """Creates hash of transaction

        Returns:
            str: hash of transaction
        """
        if self.hash == None:
            to_hash = str(self.to_json_contents())
            self.hash = sha256(to_hash.encode('utf-8')).hexdigest()
        return self.hash
        

    def to_json_contents(self):
        """ Returns a JSON-serializable representation of the contents. """
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
        """Returns a JSON-serializable representation of this object.

        Returns:
            dict: transaction representation
        """
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




    def verify(self, input_transaction, unspent, count):
        """Verifys the transaction has not already been spent and the signature is correct

        Args:
            input_transaction (Transaction): transaction to check
            unspent (list of Transaction): list of unspent transactions
            count (int): count of which input transaction to check

        Returns:
            bool: verified
        """
        verified_unspent = self.verify_unspent(input_transaction, unspent)
        if verified_unspent == False:
            return False

        # Get key from the output
        inp_script_pub_key = input_transaction.outputs[0].script_pub_key
        inp_key_array = inp_script_pub_key.split(':')

        if inp_key_array[0] == "P2PK" or inp_key_array[0] == "MULTIP2PK":
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

        signature = self.inputs[count].script_sig

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
        """verify if transaction has been spent or not

        Args:
            input_transaction (Transaction): transaction to check
            unspent (list of Transaction): list of unspent transactions

        Returns:
            bool: unspent
        """
        if self.type == 'MAIN':
            if input_transaction not in unspent:
                print('This transaction is already spent')
                return False
            else:
                print('This transaction has not yet been spent')
                return True



    def check_addr(self, addr):
        """Checks the address checksum is correct for the rest of the address

        Args:
            addr (str): address

        Returns:
            bool: the address is valid
        """
        addr_split= addr.split('+')

        check_string = addr_split[0] + '+' + addr_split[1] + '+'

        check_cs = sha256(check_string.encode('utf-8')).hexdigest()[:8]

        if check_cs == addr_split[2]:
            return True
        else:
            return False
    
    def addr_to_pub(self, addr):
        """Turns the address back into the public key

        Args:
            addr (str): public key secure

        Returns:
            str: pub_key_str
        """
        addr_array = addr.split('+')
        bytex = base58.b58decode(addr_array[0].encode('utf-8'))
        bytey = base58.b58decode(addr_array[1].encode('utf-8'))

        x= int.from_bytes(bytex, 'big')
        y= int.from_bytes(bytey, 'big')

        pub_key_str = str(x) + "+" +str(y)

        return pub_key_str


    def to_txt(self):
        """Creates a .txt file to show the transaction
        """
        try:
            os.remove('text/transaction_file.txt')
        except:
            pass
        text = self.txt_format()
        file = open('text/transaction_file.txt', 'w')
        file.write(text)
        file.close()

        filepath = 'text/transaction_file.txt'
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(filepath)
        else:                                   # linux variants
            subprocess.call(('xdg-open', filepath))
    
    def txt_format(self):
        """Returns the transaction in.txt format

        Returns:
            str: .txt representation of Transaction
        """
        text= 'Transaction: '+ self.hash + '\n'+'Value: '+ str(self.outputs[0].value)+ '\n'+'Timestamp: '+ str(self.timestamp)+ '\n'+'Type: '+self.type+ '\n- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n'+'Inputs: '

        for i in range (len(self.inputs)):
            text = text+'\n'+ str(i+1)+'.' + self.inputs[i].to_txt_format()
        
        text = text + '\nOutput:'+ self.outputs[0].to_txt_format()

        return text