from collections import namedtuple
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
