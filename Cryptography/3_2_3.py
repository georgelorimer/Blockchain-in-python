# making addresses

from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa
import base58
from hashlib import sha256

f = open('mypublickey.pem','rt')
public_key = ECC.import_key(f.read())

print(public_key)

print('\n\n\n', public_key.pointQ.xy,'\n\n\n')

x = public_key.pointQ.x
y = public_key.pointQ.y

intx = int(x)
inty = int(y)

x58 = base58.b58encode_int(intx).decode("utf-8")
y58 = base58.b58encode_int(inty).decode("utf-8")

string = str(x58) + '0' + str(y58) + '0'

hash = sha256(string.encode('utf-8')).hexdigest()

checksum = hash[:8]
print(string)
print(hash)
print(checksum)

address = string + checksum
print(address)
