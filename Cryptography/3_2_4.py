from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa
import base58
from hashlib import sha256

def pub_to_addr(pub):


    print(pub)

    x = pub.pointQ.x
    y = pub.pointQ.y

    intx = int(x)
    inty = int(y)

    x58 = base58.b58encode_int(intx).decode("utf-8")
    y58 = base58.b58encode_int(inty).decode("utf-8")

    string = str(x58) + '_' + str(y58) + '_'

    hash = sha256(string.encode('utf-8')).hexdigest()

    checksum = hash[:8]
    print('address-checksum:',string)

    print('checksum:',checksum)

    address = string + checksum
    print('address:',address)

    return address


def check_addr(addr):
    # validate checksum
    addr_split= addr.split('_')

    check_string = addr_split[0] + '_' + addr_split[1] + '_'

    check_cs = sha256(check_string.encode('utf-8')).hexdigest()[:8]
    
    if check_cs == addr_split[2]:
        return [addr_split[0],addr_split[1]]
    else:
        return None



def addr_to_pub(addr):
    
    pub_xy = check_addr(addr)
    
    bytex = base58.b58decode(pub_xy[0].encode('utf-8'))
    bytey = base58.b58decode(pub_xy[1].encode('utf-8'))

    x= int.from_bytes(bytex, 'big')
    y= int.from_bytes(bytey, 'big')

    print(x,y)

    pub = ECC.construct(curve='ed25519', point_x = x, point_y = y)
    print(pub)
    return pub







f = open('mypublickey.pem','rt')
public_key = ECC.import_key(f.read())

address = pub_to_addr(public_key)

pub_checked = addr_to_pub(address)

if public_key == pub_checked:
    print('wow')
