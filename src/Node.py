import socket
import threading
import sys
import time

from Crypto.PublicKey import ECC

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
        self.transaction_pool = Transaction_Pool()

        self.generate_keys()

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
                    self.transaction_pool.add(transaction)

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
            choice = input('Type "T" to create a transaction: ')
            if choice == "T":
                ############# ADD VALIDATION ##############
                transaction_hash = input('transaction_hash: ')
                output_id = input('output_id: ')
                script_sig = input('script_sig: ')
                script_pub_key = input('script_pub_key: ')
                value = input('value: ')
                t = Transaction(None,[Transaction_Input(transaction_hash, output_id, script_sig)],[Transaction_Output(script_pub_key, value)], datetime.now())
                self.transaction_pool.add(t)
                print("\n\n\nThis is my Transaction Pool: ", self.transaction_pool.list)
                prefixed_message="TRANSACTION:" + str(t.to_json_complete())
                self.transaction_messages.append(prefixed_message)
                self.send_message(prefixed_message)
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


if (len(sys.argv)) == 2:
    p = Node(int(sys.argv[1]),None)

elif (len(sys.argv)) == 3:
    p = Node(int(sys.argv[1]), sys.argv[2])