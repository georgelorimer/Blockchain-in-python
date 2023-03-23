import socket
import threading
import sys
import subprocess, os, platform
from datetime import timedelta, datetime
import time as tim
from hashlib import sha256

from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa
import base58



class Node:
    """Node class stores the attributes required for the p2p network and blockchain

    :ivar gui: Gui object for exit
    :vartype gui: Gui
    :ivar port: port that node is connected to
    :vartype port: int
    :ivar sock: port socket
    :vartype sock: socket
    :ivar peers: list of peers
    :vartype peers: list of int
    :ivar network_messages: list of messages in system
    :vartype network_messages: list of str
    :ivar peer_ports: list of peer ports
    :vartype peer_ports: list of int
    :ivar peer_dict: dictionary connecting peer:port
    :vartype peer_dict: dict
    :ivar balance: acount balance
    :vartype balance: int
    :ivar unspent: unspent transactions in the system
    :vartype unspent: list of Transaction
    :ivar my_unspent: my unspent transactions
    :vartype my_unspent: list of transactions
    :ivar last_transaction: last transaction sent in system
    :vartype last_transaction: str
    :ivar event_messages: message to be shown on gui.home
    :vartype event_messages: str
    :ivar transaction_pool: transaction pool of node
    :vartype transaction_pool: Transaction
    :ivar private_key: private key of user
    :vartype private_key: Key
    :ivar public_key: public key of the user
    :vartype public_key: Key
    :ivar pub_key_str: string representation of the public key
    :vartype pub_key_str: str
    :ivar blockchain: Blockchain object, personal copy of the blockchain
    :vartype blockchain: Blockchain
    :ivar eligible: bool if the block is eligible to send transactions
    :vartype eligible: bool
    :ivar mining: bool toggle mining on/off
    :vartype mining: bool
    :ivar block_found: bool whether a new block has been found or not
    :vartype block_found: str
    

    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def __init__(self, port, connection, gui):
        """innit

        Args:
            port (int): port to connect to
            connection (int): port of peer to connect to
            gui (Gui): Gui for the exit function
        """
        self.gui = gui
        self.port = port
        self.sock.bind(('127.0.0.1', port))
        self.sock.listen(5)
        self.peers = []
        self.network_messages = []
        self.peer_ports = []
        self.peer_dict = {}
        self.balance = 0
        self.last_transaction = None
        self.event_messages = None

        self.generate_keys()
        self.transaction_pool = Transaction_Pool(self.pub_key_str)

        # Connects to Genesis Peer
        if connection is not None:
            self.connect_to_peer(int(connection))
            self.blockchain = None
            self.eligible = False
            self.mining = False
        else:
            # Create Blockchain
            self.blockchain = Blockchain(None)
            date = self.blockchain.head().time
            dt = datetime(date[0], date[1], date[2], date[3], date[4], date[5], date[6])
            self.time_for_next_round =  dt + timedelta(0,60)
            self.eligible = True
            self.mining = True
        

        # for mining
        self.block_found = False 

        min_thread = threading.Thread(target=self.miner)
        min_thread.daemon = True
        min_thread.start()

        # start loop for listening to connections
        listen_thread = threading.Thread(target=self.listen)
        listen_thread.daemon = True
        listen_thread.start()

    #### LOOPING FUNCTIONS ####

    def listen(self):
        """Listens for connections and creates new thread for each connection
        """
        while True:
            c, a = self.sock.accept()

            c_thread = threading.Thread(target=self.handler, args=(c, a))
            c_thread.daemon = True
            c_thread.start()
            
            self.peers.append(c)

 
    def handler(self, c, a):
        """Handles all of the messages in the system

        TRANSACTION - For recieving new transactions
        BLOCK- For recieving new blocks
        CHAIN - For recieving a chain
        PORT - For connecting to the new port number
        EXIT - For checking which socket has left the system

        Args:
            c (socket): new socket object
            a (list): remote address
        """
        message_q = []
        while True:
            try:
                if len(message_q) == 0:

                    # try, except:
                    data = c.recv(65536)

                    str_data = data.decode("utf-8")

                    m_array = str_data.split('€')

                    str_data = m_array[0]
                    for i in range(1, len(m_array)-1):
                        message_q.append(m_array[i])


                else:
                    str_data = message_q[0]
                    message_q.pop(0)

                if str_data.startswith("TRANSACTION"):

                    if str_data not in self.network_messages and self.eligible == True:
                        str_array = str_data.split(':', 1)
                        self.network_messages.append(str_data)

                        transaction_dict = eval(str_array[1])
                        transaction = Transaction.from_json_compatible(transaction_dict)

                        if transaction.type == 'MAIN':
                            self.last_transaction = transaction

                        self.utxo()
                        count = 0
                        for input in transaction.inputs:
                            input_transaction = None
                            input_hash = input.transaction_hash
                            for t in self.unspent:
                                if t.hash == input_hash:
                                    input_transaction = t
                                    break
                            
                            
                            # change this part
                            verified = True
                            if input_hash == "GENERATED_HASH" or input_hash == 'COINBASE_TRANSACTION' or transaction.outputs[0].script_pub_key == 'BLOCK_CREATOR':
                                pass
                            else:
                                if input_transaction == None:
                                    verified = False
                                else:
                                    verified = transaction.verify(input_transaction, self.unspent.copy(), count) 
                            count += 1

                        
                        if verified == True:
                            self.transaction_pool.add(transaction)
                            self.utxo()
                            if transaction in self.my_unspent and transaction.type == 'MAIN':
                                self.event_messages = 'You recieved '+str(transaction.outputs[0].value)+' Greckles!'
                            self.send_message(str_data)
                        
                elif str_data.startswith("BLOCK"):
                    if str_data not in self.network_messages:
                        self.block_found = True
                        str_array = str_data.split(':', 1)
                        self.network_messages.append(str_data)
                        block_dict = eval(str_array[1])
                        block = Block.from_json_compatible(block_dict)

                        added = self.blockchain.add(block)
                        if added == True:
                            self.transaction_pool.update_from_block(block)

                            date = block.time
                            dt = datetime(date[0], date[1], date[2], date[3], date[4], date[5], date[6])
                            self.time_for_next_round = dt + timedelta(0, 60)
                            self.utxo()
                            if self.eligible == False:
                                self.block_found = False
                                self.eligible = True

                            self.event_messages = 'You recieved a new block'
                            self.send_message(str_data)
                        
                
                elif str_data.startswith("CHAIN"):
                    if str_data not in self.network_messages and self.blockchain == None:
                        str_array = str_data.split(':', 1)
                        self.network_messages.append(str_data)
                        blockchain_dict = eval(str_array[1])
                        self.blockchain = Blockchain.from_json_compatible(blockchain_dict)
                        
                        date = self.blockchain.head().time
                        dt = datetime(date[0], date[1], date[2], date[3], date[4], date[5], date[6])
                        self.time_for_next_round =  dt + timedelta(0,60)
                        self.utxo()
                
                elif str_data.startswith("PORT"):
                    str_array = str_data.split(':')
                    if int(str_array[1]) in self.peer_ports:
                        pass
                    else:
                        if int(str_array[1]) != int(str(self.port)):
                            
                            self.connect_to_peer(int(str_array[1]))
                            self.event_messages = 'You connected to Port: '+str(str_array[1])
                            
                            self.network_messages.append(str_data)
                            self.send_message(str_data)

                            try:
                                if self.blockchain != None:

                                    message = "CHAIN:" + str(self.blockchain.to_json_compatible())
                                    self.network_messages.append(message)
                                    self.send_message(message)
                            except:
                                pass
                
                elif str_data.startswith('EXIT'):
                    if str_data not in self.network_messages:
                        self.network_messages.append(str_data)
                        tim.sleep(0.5)
                        self.send_message(str_data)
                        if self.eligible == False and len(self.peer_ports) == 0:
                            self.gui.exit(False)
            except:
                pass



    def miner(self):
        """Mining tries to create a new block when the new round begins.
        It attempts to beet the other nodes in creating a valid block.
        If it wins it will add the block to their personal chain and then send it across the p2p network
        """
        while True:
            
            if self.mining == True and datetime.now() > self.time_for_next_round and self.eligible == True:
                b = Block.create(self.transaction_pool, self.blockchain.prev_block_hash(), self.pub_key_str)
                if self.block_found == False:
                    
                    # send Block to others
                    prefixed_message="BLOCK:" + str(b.to_json_complete())
                    self.network_messages.append(prefixed_message)
                    self.send_message(prefixed_message)

                    added = self.blockchain.add(b)
                    if added == True:
                        self.transaction_pool.update_from_block(b)

                        date = b.time
                        dt = datetime(date[0], date[1], date[2], date[3], date[4], date[5], date[6])
                        self.time_for_next_round =  dt + timedelta(0,60)
                        self.utxo()
                        self.event_messages = 'You mined a new block and recieved '+str(b.block_transactions[0].outputs[0].value)+' Greckles!'
                elif self.block_found == True:
                    self.block_found = False

    #### MENU FUNCTIONS ####
    def gen_coins(self):
        """Generates 100 coins for the user
        """

        t = Transaction(None,[Transaction_Input("GENERATED_HASH", 'None')], [Transaction_Output("P2PK:" + self.pub_key_str, 100)], datetime.now(), 'GEN')
        self.last_transaction = t
        self.transaction_pool.add(t)
        prefixed_message="TRANSACTION:" + str(t.to_json_complete())
        self.network_messages.append(prefixed_message)
        self.send_message(prefixed_message)
        self.utxo()
        self.event_messages = 'You Generated 100 Greckles!'
    
    def transaction_maker(self, transaction_to_spend, script_pub_key, value, transaction_fee, to_spend_value):
        """Creates a transaction, the change transaction and the fee transaction

        Args:
            transaction_to_spend (list of Transaction or Transaction): the selected transaction(s) to send
            script_pub_key (str): script_pub_key of the transactions
            value (int): value of the new main transaction
            transaction_fee (int): the value of the transaction fee
            to_spend_value (int): sum of the values of the transactions in transaction_to_spend

        Returns:
            bool: transaction creation succesful
        """
        inputs = []
        for transaction in transaction_to_spend:
            transaction_hash = transaction.hash

            signer = eddsa.new(self.private_key, 'rfc8032')
            script_sig = signer.sign(str(transaction.to_json_complete()).encode('utf-8'))
            inputs.append(Transaction_Input(transaction_hash, script_sig))
        
        # Main Transaction
        transaction_main = Transaction(None,inputs,[Transaction_Output(script_pub_key, value)], datetime.now(), 'MAIN')
        self.last_transaction = transaction_main

        if isinstance(transaction_to_spend, list):
            count = 0
            for transaction in transaction_to_spend:
                verified = transaction_main.verify(transaction, self.unspent.copy(), count)
                count += 1
                if verified == False:
                    break
        else:
            verified = transaction_main.verify(transaction_to_spend, self.unspent.copy(), 0)

        if verified == True:
            self.transaction_pool.add(transaction_main)
            prefixed_message="TRANSACTION:" + str(transaction_main.to_json_complete())
            self.network_messages.append(prefixed_message)
            self.send_message(prefixed_message)
            self.last_transaction = transaction_main
            self.utxo()
            

            # Change Transaction
            remaining = to_spend_value - value - transaction_fee
            if remaining > 0:
                t = Transaction(None,inputs,[Transaction_Output("P2PK:" + self.pub_key_str, remaining)], datetime.now(), 'CHANGE')
                if isinstance(transaction_to_spend, list):
                    count = 0
                    for transaction in transaction_to_spend:
                        verified = t.verify(transaction, self.unspent.copy(), count)
                        count += 1
                        if verified == False:
                            break
                else:
                    verified = t.verify(transaction_to_spend, self.unspent.copy(), 0)
                self.transaction_pool.add(t)
                prefixed_message="TRANSACTION:" + str(t.to_json_complete())
                self.network_messages.append(prefixed_message)
                self.send_message(prefixed_message)

            # Fee Transaction
            if transaction_fee == 0:
                return True
            else:
                t = Transaction(None,[Transaction_Input(transaction_hash, 'TRANSACTION_FEE')],[Transaction_Output("BLOCK_CREATOR", transaction_fee)], datetime.now(), 'FEE')
                self.transaction_pool.add(t)
                prefixed_message="TRANSACTION:" + str(t.to_json_complete())
                self.network_messages.append(prefixed_message)
                self.send_message(prefixed_message)
                self.event_messages = 'You sent '+str(transaction_main.outputs[0].value)+' Greckles!'
                return True
        else:
            return False

    #### UTILITY FUNCTIONS ####

    def connect_to_peer(self, peer_port):
        """Connect to a peer via a port number

        Args:
            peer_port (int): port to connect to
        """
        peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_sock.connect(('127.0.0.1', peer_port))
        self.peers.append(peer_sock)
        self.peer_ports.append(peer_port)
        self.peer_dict[peer_sock] = peer_port
        message = "PORT:" + str(self.port) + '€'
        peer_sock.send(bytes(message, 'utf-8'))

    def send_message(self, message):
        """Sends a message to all peers and removes broken connections

        Args:
            message (str): message to send
        """
        message = message + "€"
        broken_connections = []
        for peer in self.peers:
            try:
                peer.send(bytes(message, 'utf-8'))
            except:
                broken_connections.append(peer)
        for peer in broken_connections:
            self.peers.remove(peer)
            try:
                port = self.peer_dict[peer]
                self.peer_ports.remove(port)
                self.peer_dict.pop(peer)
            except:
                pass
        if broken_connections:
            for peer in self.peers:
                try:
                    peer.send(bytes(message, 'utf-8'))
                except BrokenPipeError:
                    broken_connections.append(peer)
            for peer in broken_connections:
                try:
                    port = self.peer_dict[peer]
                    self.peer_ports.remove(port)
                    self.peer_dict.pop(peer)
                except:
                    pass

    def generate_keys(self):
        """Generates the keys for the node
        """
        self.private_key = ECC.generate(curve='ed25519')
        self.public_key = self.private_key.public_key()
        self.pub_key_str = str(self.public_key.pointQ.x) + '+' + str(self.public_key.pointQ.y)

    def regenerate_keys(self):
        """Regenerates new keys and sends the nodes unspent transactions to the new key
        """
        self.utxo()
        new_private_key = ECC.generate(curve='ed25519')
        new_public_key = new_private_key.public_key()
        new_pub_key_str = str(new_public_key.pointQ.x) + '+' + str(new_public_key.pointQ.y)

        inputs = []
        value = 0
        if self.my_unspent == None or len(self.my_unspent) == 0:
            pass
        else:
            cp_my_unspent = self.my_unspent.copy()
            for transaction in cp_my_unspent:
                value += transaction.outputs[0].value
                transaction_hash = transaction.hash

                signer = eddsa.new(self.private_key, 'rfc8032')
                script_sig = signer.sign(str(transaction.to_json_complete()).encode('utf-8'))
                inputs.append(Transaction_Input(transaction_hash, script_sig))
            
            transaction_main = Transaction(None,inputs,[Transaction_Output('MULTIP2PK:'+new_pub_key_str, value)], datetime.now(), 'MAIN')
            self.last_transaction = transaction_main

            count = 0
            for transaction in cp_my_unspent:
                verified = transaction_main.verify(transaction, self.unspent.copy(), count)
                count += 1
                if verified == False:
                    break
            
            if verified == True:
                self.transaction_pool.add(transaction_main)
                prefixed_message="TRANSACTION:" + str(transaction_main.to_json_complete())
                self.network_messages.append(prefixed_message)
                self.send_message(prefixed_message)
                self.utxo()
        
        self.private_key = new_private_key
        self.public_key = new_public_key
        self.pub_key_str = new_pub_key_str
        self.event_messages = "You created a new private key"



    def utxo(self):
        """Updates the balance, unspent and my unspent by checking the transactions in the blockchain and transaction pool.
        """
        while not self.blockchain:
            pass

        # list of all transactions in blockchain and transaction pool - genesis block
        all_transactions = self.blockchain.return_transactions() + self.transaction_pool.list_of_transactions()
        if len(all_transactions) == 0:
            self.my_unspent = None
        else:
            unspent = []

            for transaction in all_transactions:
                if transaction.type == "GEN" or transaction.type == 'COINBASE' or transaction.type == 'CHANGE':
                    unspent.append(transaction)
                else:
                    if transaction.type == "MAIN":
                        # remove spent transaction
                        spent_array = []
                        for spent in unspent:
                            for input in transaction.inputs:
                                if spent.hash == input.transaction_hash:
                                    spent_array.append(spent)
                        
                        for spent in spent_array:
                            unspent.remove(spent)

                        # add main transaction
                        unspent.append(transaction)
            
            my_unspent = []
            balance = 0


            for transaction in unspent:
                output_key = None
                transaction_key = transaction.outputs[0].script_pub_key

                out_key_array = transaction_key.split(':')

                if out_key_array[0] == "P2PK" or out_key_array[0] == "MULTIP2PK":
                    output_key = out_key_array[1]
                
                if out_key_array[0] == "P2PKS":
                    output_key = self.addr_to_pub(out_key_array[1])

                if output_key == self.pub_key_str:
                    my_unspent.append(transaction)
                    balance += transaction.outputs[0].value
            

            self.unspent = unspent
            self.my_unspent = my_unspent
            self.balance = balance

    #### KEY SECURE FUNCTIONS 
    def pub_to_addr(self, key):
        """Turns the public key into a secure public key/address

        Args:
            key (str): pub_key_str

        Returns:
            str: public key secure
        """
        pub_array = key.split('+')
        intx = int(pub_array[0])
        inty = int(pub_array[1])

        x58 = base58.b58encode_int(intx).decode("utf-8")
        y58 = base58.b58encode_int(inty).decode("utf-8")

        string = str(x58) + '+' + str(y58) + '+'

        hash = sha256(string.encode('utf-8')).hexdigest()

        checksum = hash[:8]

        address = string + checksum

        return address
    
    def check_addr(self, addr):
        """Checks the address checksum is correct for the rest of the address

        Args:
            addr (str): address

        Returns:
            bool: the address is valid
        """
        addr_split= addr.split('+')

        check_string = addr_split[0] + '+' + addr_split[1] + '+'

        check_cs = sha256(check_string.encode('utf-8')).hexdigest()[:8]

        if check_cs == addr_split[2]:
            return True
        else:
            return False
    
    def addr_to_pub(self, addr):
        """Turns the address back into the public key

        Args:
            addr (str): public key secure

        Returns:
            str: pub_key_str
        """
        addr_array = addr.split('+')
        bytex = base58.b58decode(addr_array[0].encode('utf-8'))
        bytey = base58.b58decode(addr_array[1].encode('utf-8'))

        x= int.from_bytes(bytex, 'big')
        y= int.from_bytes(bytey, 'big')

        pub_key_str = str(x) + "+" +str(y)

        return pub_key_str


    def unspent_to_txt(self):
        """Creates a .txt file that outputs the unspent transactions
        """
        try:
            self.utxo()
            file = open('text/unspent_transactions.txt', 'w')
            file.write('Unspent Transactions:')
            for i in range(len(self.my_unspent)):
                file.write('\n------------------------------------------------------------------------------\n')
                file.write('Transaction '+ str(i+1)+ ': \n')
                file.write(self.my_unspent[i].txt_format())

            file.close()
            filepath = 'text/unspent_transactions.txt'
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', filepath))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(filepath)
            else:                                   # linux variants
                subprocess.call(('xdg-open', filepath))
        except:
            pass