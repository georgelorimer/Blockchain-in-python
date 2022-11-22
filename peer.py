import socket
import threading
import sys

class Peer:
    # Creates socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # bind socket to port
    def __init__(self,port):
        self.sock.bind(('127.0.0.1', port))
        self.connections = []
        self.sock.listen(3)
        self.disconnect= False
        if port != 1234:
            self.sock.connect(("127.0.0.1", 1234))

        # while loop to listen for connections and set up threads
        while True:
            c, a = self.sock.accept()
            handlerThread = threading.Thread(target=self.handler, args=(c,a))
            handlerThread.daemon = True
            handlerThread.start()

            msgThread = threading.Thread(target=self.sendMsg)
            msgThread.daemon = True
            msgThread.start()

            self.connections.append(c)
            self.sock.connect(('127.0.0.1', a[1]))
            print(self.connections)
    
    # handles incoming messages
    def handler(self,c, a):
        while True:
            data = c.recv(1024)
            for connection in self.connections:
                connection.send(bytes(data))
            if not data:
                self.connections.remove(c)
                c.close()
                break
    
    # sends messages to connections
    def sendMsg(self):
        while True:
            self.sock.send(bytes(input(''), 'utf-8'))

# self.?
    #     listenThread = threading.Thread(target=self.listen)
    #     listenThread.daemon = True
    #     listenThread.start()

    #     while True:


    # def listen():


peer = Peer(int(sys.argv[1]))
if sys.argv[1] != 1234:
    peer.sock.connect(("127.0.0.1", 1234))