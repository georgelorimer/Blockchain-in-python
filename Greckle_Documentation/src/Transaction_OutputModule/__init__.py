from collections import namedtuple
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