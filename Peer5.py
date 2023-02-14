import socket
import threading
import sys
import time

class Peer:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def __init__(self, port, connection):
        self.port = port
        self.sock.bind(('127.0.0.1', port))
        self.sock.listen(5)
        self.peers = []
        self.messages = []
        self.peer_ports = []
        self.peer_dict = {}

        # Connects to Genesis Peer --> DIF
        if connection is not None:
            self.connect_to_peer(int(connection))

        m_thread = threading.Thread(target=self.send_message)
        m_thread.daemon = True
        m_thread.start()

        # start loop for listening to connections
        self.listen()

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


    # sets up a new handler for each connection
    def handler(self, c, a):
        while True:
            data = c.recv(1024)
            str_data = data.decode("utf-8")

            if str_data.startswith("MSG"):
                if str_data not in self.messages:
                    self.messages.append(str_data)
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
    
    def send_message(self):
        while True:
            # waiting for message
            broken_connections = []
            message = input('')
            prefixed_message="MSG:" + message
            for peer in self.peers:
                try:
                    peer.send(bytes(prefixed_message, 'utf-8'))
                except:
                    broken_connections.append(peer)
            print('BROKEN CONNECTIONS:', broken_connections)
            print(self.peer_dict)
            for peer in broken_connections:
                print(self.peers)
                self.peers.remove(peer)
                try:
                    print('1')
                    port = self.peer_dict[peer]
                    print('2')
                    self.peer_ports.remove(port)
                    print('3')
                    self.peer_dict.pop(peer)
                    print('4')
                except:
                    pass
            print('After testing',self.peer_dict)
            print(self.peer_ports)
            if broken_connections:
                for peer in self.peers:
                    try:
                        peer.send(bytes(prefixed_message, 'utf-8'))
                    except BrokenPipeError:
                        broken_connections.append(peer)
                print('BROKEN CONNECTIONS:', broken_connections)
                print(self.peer_dict)
                for peer in broken_connections:
                    try:
                        print('1')
                        port = self.peer_dict[peer]
                        print('2')
                        self.peer_ports.remove(port)
                        print('3')
                        self.peer_dict.pop(peer)
                        print('4')
                    except:
                        pass
                print('After testing',self.peer_dict)
                print(self.peer_ports)

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

    


if (len(sys.argv)) == 2:
    p = Peer(int(sys.argv[1]),None)
    p.run()

elif (len(sys.argv)) == 3:
    p = Peer(int(sys.argv[1]), sys.argv[2])
    p.run()