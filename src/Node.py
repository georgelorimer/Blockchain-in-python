import socket
import threading
import sys
import time

from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa

from Transaction import *
from Transaction_Collections import *

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

        m_thread = threading.Thread(target=self.menu)
        m_thread.daemon = True
        m_thread.start()

        # MINING THREAD

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
            print(self.peers)
            print(self.peer_ports)
            print(f'Connected to peer at {a[0]}:{a[1]}')


    # sets up a new handler for each connection 
    def handler(self, c, a):
        while True:
            data = c.recv(1024)
            str_data = data.decode("utf-8")

            if str_data.startswith("TRANSACTION"):
                if str_data not in self.transaction_messages:
                    str_array = str_data.split(':', 1)
                    self.transaction_messages.append(str_data)

                    # This is where I will call the functions to make a transaction from message
                    transaction_dict = eval(str_array[1])
                    transaction = Transaction.from_json_compatible(transaction_dict)
                    ######################################## VERIFY #####################################

                    input_hash = transaction.inputs[0].transaction_hash
                    for t in self.transaction_pool.transactions_unspent.unspent:
                        if t.get_hash() == input_hash:
                            input_transaction = t
                            break
                    if transaction.inputs[0].transaction_hash != "GENERATED_HASH":
                        transaction.verify(input_transaction)
                    self.transaction_pool.add(transaction)
                    if transaction.inputs[0].transaction_hash != "GENERATED_HASH":
                        self.transaction_pool.transactions_unspent.spent(input_transaction)


                    print("\n\n\nThis is my Transaction Pool: ", self.transaction_pool.list)

                    print(data)
                    for peer in self.peers:
                        try:
                            peer.send(data)
                        except:
                            pass
            
            elif str_data.startswith("PORT"):
                str_array = str_data.split(':')
                print(str_array)
                if int(str_array[1]) in self.peer_ports:
                    pass
                else:
                    if int(str_array[1]) != int(str(self.port)):
                        
                        self.connect_to_peer(int(str_array[1]))
                        time.sleep(1)

                        for peer in self.peers:
                            peer.send(data)

    def menu(self):
        while True:
            choice = input('Type one of the following choices:\n\t"T" to create a transaction\n\t"G" to generate 100 coins\n\t"A" to see your balance\n\t"U" to show the unspent transactions that you can spend:\n\t"K" to get your public key: ')
            if choice == "T":
                counter = 1
                print("Unspent Transactions:")
                for transaction in self.transaction_pool.transactions_unspent.my_unspent:
                    print(counter, '.\t', transaction.to_json_complete())
                    counter += 1
                transaction_choice = int(input('Choose your transaction to spend: '))
                transaction_to_spend = self.transaction_pool.transactions_unspent.my_unspent[transaction_choice - 1]

                ############# ADD VALIDATION ##############
                # inputs
                transaction_hash = transaction_to_spend.hash
                output_id = 0 # <------ FOR NOW
                signer = eddsa.new(self.private_key, 'rfc8032')
                script_sig = signer.sign(str(transaction_to_spend.to_json_complete()).encode('utf-8'))

                #outputs
                script_pub_key = input('Enter the public key of the desired recipient: ')
                value = int(input("Ammount to send: "))

                try:
                    t = Transaction(None,[Transaction_Input(transaction_hash, output_id, script_sig)],[Transaction_Output(script_pub_key, value)], datetime.now())
                    ######################################## VERIFY #####################################
                    t.verify(transaction_to_spend)
                    self.transaction_pool.add(t)
                    print("\n\n\nThis is my Transaction Pool: ", self.transaction_pool.list)
                    prefixed_message="TRANSACTION:" + str(t.to_json_complete())
                    self.transaction_messages.append(prefixed_message)
                    self.send_message(prefixed_message)
                    self.transaction_pool.transactions_unspent.spent(transaction_to_spend)
                except:
                    print('Invalid transaction')

                if transaction_to_spend.outputs[0].value > value: #-----> change [0]
                    remaining = transaction_to_spend.outputs[0].value - value#-----> change [0]
                    try:
                        t = Transaction(None,[Transaction_Input(transaction_hash, output_id, script_sig)],[Transaction_Output(self.pub_key_str, remaining)], datetime.now())
                        t.verify(transaction_to_spend)
                        self.transaction_pool.add(t)
                        print("\n\n\nThis is my Transaction Pool: ", self.transaction_pool.list)
                        prefixed_message="TRANSACTION:" + str(t.to_json_complete())
                        self.transaction_messages.append(prefixed_message)
                        self.send_message(prefixed_message)
                    except:
                        print('Invalid Transactions')
            

            elif choice == 'G':
                pub_key_str= str(self.public_key.pointQ.x) + '+' + str(self.public_key.pointQ.y)
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


    #### UTILITY FUNCTIONS ####

    def connect_to_peer(self, peer_port):
        peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_sock.connect(('127.0.0.1', peer_port))
        self.peers.append(peer_sock)
        self.peer_ports.append(peer_port)
        self.peer_dict[peer_sock] = peer_port
        print(self.peer_dict)
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
        # Look in 3_2.py for exporting key as pem
        self.private_key = ECC.generate(curve='ed25519')
        self.public_key = self.private_key.public_key()
        self.pub_key_str = str(self.public_key.pointQ.x) + '+' + str(self.public_key.pointQ.y)


if (len(sys.argv)) == 2:
    p = Node(int(sys.argv[1]),None)

elif (len(sys.argv)) == 3:
    p = Node(int(sys.argv[1]), sys.argv[2])