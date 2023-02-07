# Generating private and public keys

from Crypto.PublicKey import ECC

key = ECC.generate(curve='ed25519')
f = open('myprivatekey.pem','wt')
f.write(key.export_key(format='PEM'))
f.close()
f = open('mypublickey.pem','wt')
f.write(key.public_key().export_key(format='PEM'))
f.close()



f = open('myprivatekey.pem','rt')
private_key = ECC.import_key(f.read())

f = open('mypublickey.pem','rt')
public_key = ECC.import_key(f.read())

print(private_key)

print(public_key)


