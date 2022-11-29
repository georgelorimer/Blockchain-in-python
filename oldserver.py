import socket
import threading
import sys

# Call this welcoming node as it welcomes nodes to network
class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connections = []
    def __init__(self):
        # server on port 1234 of this computer
        self.sock.bind(('127.0.0.1', 1234))

        self.sock.listen(1)


    def handler(self,c, a):
        global connections
        while True:
            data = c.recv(1024)
            for connection in self.connections:
                connection.send(bytes(data))
            if not data:
                connections.remove(c)
                c.close()
                break

    def run(self):
        while True:
            c, a = self.sock.accept()
            cThread = threading.Thread(target=self.handler, args=(c,a))
            cThread.daemon = True
            cThread.start()

            self.connections.append(c)
            print (a[1])
            print(self.connections)

class Client:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    def __init__(self, port):
        self.sock.bind(('127.0.0.1', port))
        self.sock.connect(('127.0.0.1', 1234))

        iThread = threading.Thread(target=self.sendMsg)
        iThread.daemon = True
        iThread.start()

        # transaction pool
        transaction_pool = []


        while True:
            data = self.sock.recv(1024)
            if not data:
                break
            print(data)
            transaction_pool.append(data)
            print(transaction_pool)

    def sendMsg(self):
        while True:
            self.sock.send(bytes(input(''), 'utf-8'))



if (len(sys.argv)) > 1:
    c = Client(int(sys.argv[1]))
else:
    s = Server()
    s.run()