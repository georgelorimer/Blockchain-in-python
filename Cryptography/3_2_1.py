# Signature

from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa

message = b'I give my permission to order #4355'
key = ECC.import_key(open("myprivatekey.pem").read())
signer = eddsa.new(key, 'rfc8032')
signature = signer.sign(message)

# sends: message, public key, signature (maybe as JSON)

# On other end

message = b'I give my permission to order #4355'
key = ECC.import_key(open("mypublickey.pem").read())
verifier = eddsa.new(key, 'rfc8032')
try:
    verifier.verify(message, signature)
    print("The message is authentic")
except ValueError:
    print("The message is not authentic")

