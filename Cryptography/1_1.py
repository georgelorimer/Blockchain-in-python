# Basic hash function usage

from hashlib import sha256

# commitment sceme
print ("0"*3)
# commit(msg, nonce) -> hash
def commit(msg, nonce) -> str:
    toHash = msg + nonce
    hashed = sha256(toHash.encode('utf-8')).hexdigest()
    return hashed

# verify(com, msg, nonce)
def verify(com, msg, nonce) -> bool:
    toCheck = msg + nonce
    hashed = sha256(toCheck.encode('utf-8')).hexdigest()
    if com == hashed:
        return True
    else:
        return False

nonce = 'ThisIsMyNonce'
input_ = input('Enter something to be hashed: ')
print(commit(input_, nonce))

checkMsg = input('Check message: ')
checkInput = input('Check input: ')
checkNonce = input('Check Nonce: ')

print(verify(checkMsg, checkInput, checkNonce))