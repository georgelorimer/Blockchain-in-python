# comapact public key and address

from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa
import base58


f = open('mypublickey.pem','rt')
public_key = ECC.import_key(f.read())

print(public_key)

print('\n\n\n', public_key.pointQ.xy,'\n\n\n')

x = public_key.pointQ.x
y = public_key.pointQ.y

intx = int(x)
inty = int(y)

print('\n\n\n', x,'\n\n\n')
print('\n\n\n', y,'\n\n\n')

print('\n\n\n', hex(x),'\n\n\n')
print('\n\n\n', hex(y),'\n\n\n')

print(base58.b58encode_int(intx))
print(base58.b58encode_int(inty))
