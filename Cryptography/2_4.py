# prrof of work function

from hashlib import sha256
from datetime import datetime

def proof_of_work(hash_pointer, target):
    nonce = 0
    found = False
    threshold = "0"*target
    starttime = datetime.now()
    while found == False:
        toHash = str(nonce) + hash_pointer
        hashed = sha256(toHash.encode('utf-8')).hexdigest()
        if hashed.startswith(threshold):
            endtime = datetime.now()
            found = True
            print (endtime - starttime)
            print (hashed)
            print (nonce)
        else:
            nonce += 1


target = 6
hash_p = "aaf9441ccbc297b3fe5c3cef201b614d46767d17412031f0099b0cb06dbf668c"

proof_of_work(hash_p, target)