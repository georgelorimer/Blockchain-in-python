import socket
import threading
import time as tim
from datetime import timedelta, datetime

from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa

from Transaction import *
from Transaction_Collections import *
from Block import *
from Blockchain import *

class Node:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def __init__(self, port, connection):
        self.port = port
        self.sock.bind(('127.0.0.1', port))
        self.sock.listen(5)
        self.peers = []
        self.transaction_messages = []
        self.peer_ports = []
        self.peer_dict = {}

        self.generate_keys()
        self.transaction_pool = Transaction_Pool(self.pub_key_str)

        # Connects to Genesis Peer
        if connection is not None:
            self.connect_to_peer(int(connection))
            self.blockchain = None
        else:
            # Create Blockchain
            self.blockchain = Blockchain(None)
            date = self.blockchain.head().time
            dt = datetime(date[0], date[1], date[2], date[3], date[4], date[5], date[6])
            self.time_for_next_round =  dt + timedelta(0,60)

        # for mining
        self.mining = False
        self.block_found = False 

        m_thread = threading.Thread(target=self.menu)
        m_thread.daemon = True
        m_thread.start()

        min_thread = threading.Thread(target=self.miner)
        min_thread.daemon = True
        min_thread.start()

        # start loop for listening to connections
        self.listen()

    #### LOOPING FUNCTIONS ####

    def listen(self):
        print(f'Peer running on port {self.port}')
        while True:
            c, a = self.sock.accept()

            c_thread = threading.Thread(target=self.handler, args=(c, a))
            c_thread.daemon = True
            c_thread.start()
            
            self.peers.append(c)
            print(f'Connected to peer at {a[0]}:{a[1]}')

 
    def handler(self, c, a):
        while True:
            # try, except:
            data = c.recv(65536)
            
            str_data = data.decode("utf-8")

            if str_data.startswith("TRANSACTION"):

                if str_data not in self.transaction_messages:
                    str_array = str_data.split(':', 1)
                    self.transaction_messages.append(str_data)

                    transaction_dict = eval(str_array[1])
                    transaction = Transaction.from_json_compatible(transaction_dict)

                    input_hash = transaction.inputs[0].transaction_hash
                    for t in self.transaction_pool.transactions_unspent.unspent:
                        if t.get_hash() == input_hash:
                            input_transaction = t
                            break
                    
                    # change this part
                    verified = True
                    if input_hash == "GENERATED_HASH" or input_hash == 'COINBASE_TRANSACTION' or transaction.outputs[0].script_pub_key == 'BLOCK_CREATOR':
                        pass
                    else:
                        verified = transaction.verify(input_transaction)
                        if verified == True:
                            self.transaction_pool.transactions_unspent.spent(input_transaction)
                    if verified == True:
                        self.transaction_pool.add(transaction)
                        self.send_message(str_data)
                    
            elif str_data.startswith("BLOCK"):
                if str_data not in self.transaction_messages:
                    self.block_found = True
                    str_array = str_data.split(':', 1)
                    self.transaction_messages.append(str_data)
                    block_dict = eval(str_array[1])
                    block = Block.from_json_compatible(block_dict)

                    self.blockchain.add(block)
                    # verify
                    self.transaction_pool.update_from_block(block)
                    
                    date = block.time
                    dt = datetime(date[0], date[1], date[2], date[3], date[4], date[5], date[6])
                    self.time_for_next_round = dt + timedelta(0, 60)

                    self.send_message(str_data)
            
            elif str_data.startswith("CHAIN"):
                if str_data not in self.transaction_messages and self.blockchain == None:
                    str_array = str_data.split(':', 1)
                    self.transaction_messages.append(str_data)
                    blockchain_dict = eval(str_array[1])
                    self.blockchain = Blockchain.from_json_compatible(blockchain_dict)
                    
                    date = self.blockchain.head().time
                    dt = datetime(date[0], date[1], date[2], date[3], date[4], date[5], date[6])
                    self.time_for_next_round =  dt + timedelta(0,60)
            
            elif str_data.startswith("PORT"):
                str_array = str_data.split(':')
                if int(str_array[1]) in self.peer_ports:
                    pass
                else:
                    if int(str_array[1]) != int(str(self.port)):
                        
                        self.connect_to_peer(int(str_array[1]))
                        tim.sleep(0.2)
                        
                        for peer in self.peers:
                            try:
                                peer.send(data)
                                tim.sleep(0.3)
                                if self.blockchain != None:

                                    message = "CHAIN:" + str(self.blockchain.to_json_compatible())
                                    self.transaction_messages.append(message)
                                    peer.send(bytes(message, 'utf-8'))
                                    tim.sleep(0.5)
                            except:
                                pass


    def menu(self):
        while True:
            choice = input('Type one of the following choices:\n\t"T" to create a transaction\n\t"G" to generate 100 coins\n\t"A" to see your balance\n\t"U" to show the unspent transactions that you can spend:\n\t"K" to get your public key\n\t"M" to toggle mining on/off\n\t"B" to create and print Block\n\t"R" for the amount of time until the next round\n\t"S" to get the blockchain and last block: ')
            if choice == "T":
                transaction_to_spend, script_pub_key, value, transaction_fee = self.transaction_input()
                transaction_hash = transaction_to_spend.hash
                output_id = 0
                signer = eddsa.new(self.private_key, 'rfc8032')
                script_sig = signer.sign(str(transaction_to_spend.to_json_complete()).encode('utf-8'))
                
                # Main Transaction
                transaction_main = Transaction(None,[Transaction_Input(transaction_hash, output_id, script_sig)],[Transaction_Output(script_pub_key, value)], datetime.now())
                transaction_main.verify(transaction_to_spend)
                self.transaction_pool.add(transaction_main)
                prefixed_message="TRANSACTION:" + str(transaction_main.to_json_complete())
                self.transaction_messages.append(prefixed_message)
                self.send_message(prefixed_message)
                self.transaction_pool.transactions_unspent.spent(transaction_to_spend)
                
                # Change Transaction
                remaining = transaction_to_spend.outputs[0].value - value - transaction_fee
                t = Transaction(None,[Transaction_Input(transaction_hash, output_id, script_sig)],[Transaction_Output(self.pub_key_str, remaining)], datetime.now())
                t.verify(transaction_to_spend)
                self.transaction_pool.add(t)
                prefixed_message="TRANSACTION:" + str(t.to_json_complete())
                self.transaction_messages.append(prefixed_message)
                self.send_message(prefixed_message)

                # Fee Transaction
                t = Transaction(None,[Transaction_Input(transaction_hash, output_id, 'TRANSACTION_FEE')],[Transaction_Output("BLOCK_CREATOR", transaction_fee)], datetime.now())
                self.transaction_pool.add(t)
                prefixed_message="TRANSACTION:" + str(t.to_json_complete())
                self.transaction_messages.append(prefixed_message)
                self.send_message(prefixed_message)
        

            elif choice == 'G':
                t = Transaction(None,[Transaction_Input("GENERATED_HASH", 0, 'None')], [Transaction_Output(self.pub_key_str, 100)], datetime.now())
                self.transaction_pool.add(t)
                prefixed_message="TRANSACTION:" + str(t.to_json_complete())
                self.transaction_messages.append(prefixed_message)
                self.send_message(prefixed_message)

            
            elif choice == "A":
                print('Balance is:', self.transaction_pool.transactions_unspent.utxo)
            
            elif choice == "U":
                counter = 1
                print("Unspent Transactions:")
                for transaction in self.transaction_pool.transactions_unspent.my_unspent:
                    print(counter, '.\t', transaction.to_json_complete())
                    counter += 1

            elif choice == "K":
                print('Your public key is:', self.pub_key_str)

            elif choice == "M":
                if self.mining == False:
                    self.mining = True
                    print('Mining is turned on')
                    print('Time till next: ', self.time_for_next_round - datetime.now())
                elif self.mining == True:
                    self.mining = False
                    print('Mining is turned off')
            
            elif choice == "B":
                b = Block.create(self.transaction_pool, 'None', self.pub_key_str)
                print(b.to_json_complete())
            
            elif choice == "R":
                print('Time till next: ', self.time_for_next_round - datetime.now())
            
            elif choice == "S":
                print("\nThis is my Blockchain:\n\n", self.blockchain.to_json_compatible())
                print("\nThis is the last block:\n\n", self.blockchain.head().to_json_complete())


    def miner(self):
        while True:
            
            if self.mining == True and datetime.now() > self.time_for_next_round:
                print('mining...')
                b = Block.create(self.transaction_pool, self.blockchain.prev_block_hash(), self.pub_key_str)
                if self.block_found == False:
                    print("\n\n\n I Won \n\n\n")
                    # send Block to others
                    prefixed_message="BLOCK:" + str(b.to_json_complete())
                    self.transaction_messages.append(prefixed_message)
                    self.send_message(prefixed_message)

                    self.blockchain.add(b)
                    self.transaction_pool.update_from_block(b)

                    date = b.time
                    dt = datetime(date[0], date[1], date[2], date[3], date[4], date[5], date[6])
                    self.time_for_next_round =  dt + timedelta(0,60)
                elif self.block_found == True:
                    print("\n\n\n I LOST \n\n\n")
                    self.block_found = False

    #### MENU FUNCTIONS ####
    def transaction_input(self):
        transaction_to_spend = None
        while transaction_to_spend == None:
            counter = 1
            print("Unspent Transactions:")
            for transaction in self.transaction_pool.transactions_unspent.my_unspent:
                print(counter, '.\t', transaction.to_json_complete())
                counter += 1
            transaction_choice = int(input('Choose your transaction to spend: '))
            if transaction_choice in range(1, len(self.transaction_pool.transactions_unspent.my_unspent)+1):
                transaction_to_spend = self.transaction_pool.transactions_unspent.my_unspent[transaction_choice - 1]
                to_spend_value = transaction_to_spend.outputs[0].value
            else:
                transaction_to_spend = None
                print("Not an option")
        
        script_pub_key = input('Enter the public key of the desired recipient: ')
        
        value = None
        while value == None:
            value = int(input("Amount to spend (Transaction amount: "+str(to_spend_value) +"): "))
            if value < to_spend_value and value > 0:
                transaction_fee = int(input("Transaction fee: "))
                if transaction_fee > 0 and (transaction_fee + value) < to_spend_value:
                    pass
                else:
                    value = None
            else:
                value = None
                print('incorrect value')
        
        return transaction_to_spend, script_pub_key, value, transaction_fee

    #### UTILITY FUNCTIONS ####

    def connect_to_peer(self, peer_port):
        peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_sock.connect(('127.0.0.1', peer_port))
        self.peers.append(peer_sock)
        self.peer_ports.append(peer_port)
        self.peer_dict[peer_sock] = peer_port
        message = "PORT:" + str(self.port)
        peer_sock.send(bytes(message, 'utf-8'))
        print(f'Connected to peer at port {peer_port}')

    def send_message(self, message):
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
        self.private_key = ECC.generate(curve='ed25519')
        self.public_key = self.private_key.public_key()
        self.pub_key_str = str(self.public_key.pointQ.x) + '+' + str(self.public_key.pointQ.y)


user_port = input("Your port: ")
peer_port = input("Peer port or 'N' if no peer: ")

if peer_port == 'N':
    p = Node(int(user_port),None)
else:
    p = Node(int(user_port), peer_port)
