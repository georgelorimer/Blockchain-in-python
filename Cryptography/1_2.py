# Hash pointers


class Block:

    def __init__(self, hash_pointer, data) -> None:
        self.hash_pointer = hash_pointer
        self.data = data

    def hash(self, msg) -> str:
        return sha256(msg.encode('utf-8')).hexdigest()



#  This has to be real block (see labchain)
GENESIS_BLOCK = Block("0", "Data for first block")

GENESIS_BLOCK_HASH = GENESIS_BLOCK.hash

class Chain:

    def __init__(self) -> None:
        self.blocks = [GENESIS_BLOCK]
        self.blocks_index_dict = {GENESIS_BLOCK_HASH: 0}

    def insert_Block(self, data) -> None:
        """
        Inserts block onto end of chain
        """
        hp_toHash = self.blocks[-1].hash_pointer + self.blocks[-1].data

        hp = sha256(hp_toHash.encode('utf-8')).hexdigest()

        block = Block(hp, data)

        self.blocks.append(block)
        self.blocks_index_dict.update({hp: len(self.blocks_index_dict)-1})


bc = Chain()
print("Genesis state of chain")
print(bc.blocks)
print(bc.blocks_index_dict)

bc.insert_Block("this is the data")
print("new state of chain")
print(bc.blocks)
print(bc.blocks_index_dict)






