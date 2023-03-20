import socket
import threading
import os
from datetime import timedelta, datetime

from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa
import base58
from hashlib import sha256

from Transaction import *
from Transaction_Pool import *
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
        self.balance = 0
        self.last_transaction = None

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

        # m_thread = threading.Thread(target=self.menu)
        # m_thread.daemon = True
        # m_thread.start()

        min_thread = threading.Thread(target=self.miner)
        min_thread.daemon = True
        min_thread.start()

        # start loop for listening to connections
        listen_thread = threading.Thread(target=self.listen)
        listen_thread.daemon = True
        listen_thread.start()

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
        message_q = []
        while True:
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

                if str_data not in self.transaction_messages and self.eligible == True:
                    str_array = str_data.split(':', 1)
                    self.transaction_messages.append(str_data)

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
                                verified = transaction.verify(input_transaction, self.unspent, count) 
                        count += 1

                    
                    if verified == True:
                        print('Success')
                        self.transaction_pool.add(transaction)
                        self.utxo()
                        self.send_message(str_data)
                    
            elif str_data.startswith("BLOCK"):
                if str_data not in self.transaction_messages:
                    self.block_found = True
                    str_array = str_data.split(':', 1)
                    self.transaction_messages.append(str_data)
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
                    self.utxo()
            
            elif str_data.startswith("PORT"):
                str_array = str_data.split(':')
                if int(str_array[1]) in self.peer_ports:
                    pass
                else:
                    if int(str_array[1]) != int(str(self.port)):
                        
                        self.connect_to_peer(int(str_array[1]))
                        
                        self.transaction_messages.append(str_data)
                        self.send_message(str_data)

                        try:
                            if self.blockchain != None:

                                message = "CHAIN:" + str(self.blockchain.to_json_compatible())
                                self.transaction_messages.append(message)
                                self.send_message(message)
                        except:
                            pass


    def menu(self):
        print('Waiting for block to be made')
        while self.eligible == False:
            pass
        while True:
            choice = input('Type one of the following choices:\n\t"T" to create a transaction\n\t"G" to generate 100 coins\n\t"A" to see your balance\n\t"U" to show the unspent transactions that you can spend:\n\t"K" to get your public key or "KS" for your secure key\n\t"M" to toggle mining on/off\n\t"B" to create and print Block\n\t"R" for the amount of time until the next round\n\t"S" to get the blockchain and last block: ')
            if choice == "T":
                self.utxo()
                if not self.my_unspent:
                    print('No transactions to use')
                else:
                    transaction_to_spend, script_pub_key, value, transaction_fee, to_spend_value = self.transaction_input()
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
                            verified = transaction_main.verify(transaction, self.unspent, count)
                            count += 1
                            if verified == False:
                                break
                    else:
                        verified = transaction_main.verify(transaction_to_spend, self.unspent, 0)

                    if verified == True:
                        self.transaction_pool.add(transaction_main)
                        prefixed_message="TRANSACTION:" + str(transaction_main.to_json_complete())
                        self.transaction_messages.append(prefixed_message)
                        self.send_message(prefixed_message)
                        self.utxo()
                        

                        # Change Transaction
                        remaining = to_spend_value - value - transaction_fee
                        t = Transaction(None,inputs,[Transaction_Output("P2PK:" + self.pub_key_str, remaining)], datetime.now(), 'CHANGE')
                        if isinstance(transaction_to_spend, list):
                            count = 0
                            for transaction in transaction_to_spend:
                                verified = t.verify(transaction, self.unspent, count)
                                count += 1
                                if verified == False:
                                    break
                        else:
                            verified = t.verify(transaction_to_spend, self.unspent, 0)
                        self.transaction_pool.add(t)
                        prefixed_message="TRANSACTION:" + str(t.to_json_complete())
                        self.transaction_messages.append(prefixed_message)
                        self.send_message(prefixed_message)


                        # Fee Transaction
                        t = Transaction(None,[Transaction_Input(transaction_hash, 'TRANSACTION_FEE')],[Transaction_Output("BLOCK_CREATOR", transaction_fee)], datetime.now(), 'FEE')
                        self.transaction_pool.add(t)
                        prefixed_message="TRANSACTION:" + str(t.to_json_complete())
                        self.transaction_messages.append(prefixed_message)
                        self.send_message(prefixed_message)
                    else:
                        print("Transaction not verified")
        

            elif choice == 'G':
                t = Transaction(None,[Transaction_Input("GENERATED_HASH", 'None')], [Transaction_Output("P2PK:" + self.pub_key_str, 100)], datetime.now(), 'GEN')
                self.last_transaction = t
                self.transaction_pool.add(t)
                prefixed_message="TRANSACTION:" + str(t.to_json_complete())
                self.transaction_messages.append(prefixed_message)
                self.send_message(prefixed_message)
            
            elif choice == "A":
                self.utxo()
                print('Balance is:', self.balance)
            
            elif choice == "U":
                self.utxo()
                counter = 1
                print("Unspent Transactions:")
                for transaction in self.my_unspent:
                    print(counter, '.\t', transaction.to_json_complete())
                    counter += 1

            elif choice == "K":
                print('Your public key is:', self.pub_key_str)
            
            elif choice == "KS":
                address = self.pub_to_addr(self.pub_key_str)
                print('Your secure key is:', address)
                print('Is valid:', self.check_addr(address))
                print('Public Key is:', self.addr_to_pub(address))

            elif choice == "M":
                if self.mining == False:
                    self.mining = True
                    print('Mining is turned on')
                    if self.eligible == False:
                        print('Not eligible to mine until the next round')
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
            
            if self.mining == True and datetime.now() > self.time_for_next_round and self.eligible == True:
                print('mining...')
                b = Block.create(self.transaction_pool, self.blockchain.prev_block_hash(), self.pub_key_str)
                if self.block_found == False:
                    
                    # send Block to others
                    prefixed_message="BLOCK:" + str(b.to_json_complete())
                    self.transaction_messages.append(prefixed_message)
                    self.send_message(prefixed_message)

                    added = self.blockchain.add(b)
                    if added == True:
                        print("\n\n\n I Won \n\n\n")
                        self.transaction_pool.update_from_block(b)

                        date = b.time
                        dt = datetime(date[0], date[1], date[2], date[3], date[4], date[5], date[6])
                        self.time_for_next_round =  dt + timedelta(0,60)
                        self.utxo()
                elif self.block_found == True:
                    print("\n\n\n I LOST \n\n\n")
                    self.block_found = False

    #### MENU FUNCTIONS ####
    def transaction_input(self):
        self.utxo()
        tried = False
        while tried == False:
            # try:
            script_choice = input('How do you want to send your coins?\n\t"P2PK" to pay to pub_key\n\t"P2PKS" to pay to pub_key with a checksum\n\t"MULTIP2PK" to pay multiple transactions to pub_key: ')
            if script_choice == "P2PK" or script_choice == "P2PKS":
                while transaction_to_spend == None:
                    counter = 1
                    print("Unspent Transactions:")
                    for transaction in self.my_unspent:
                        print(counter, '.\t', transaction.to_json_complete())
                        counter += 1
                    transaction_choice = int(input('Choose your transaction to spend: '))
                    if transaction_choice in range(1, len(self.my_unspent)+1):
                        transaction_to_spend = self.my_unspent[transaction_choice - 1]
                        to_spend_value = transaction_to_spend.outputs[0].value
                    else:
                        transaction_to_spend = None
                        print("Not an option")
            
            elif script_choice == "MULTIP2PK":
                transaction_to_spend = []
                
                while transaction_to_spend == []:
                    to_spend_value = 0
                    print("Select a transction to spend by typing the number next to it, when you have selected all the transactions you want to use, enter 'x'")
                    print('Unspent Transactions:')
                    counter = 1
                    for transaction in self.my_unspent:
                        print(counter, '.\t', transaction.to_json_complete())
                        counter += 1
                    
                    completed = False
                    while completed == False:
                        print('Current amount to spend:', to_spend_value)
                        transaction_choice = input('Choose your transaction to spend: ')
                    
                        if transaction_choice == 'x':
                            if len(transaction_to_spend) == 0:
                                print('Please select at least 1 transaction to spend')
                            else:
                                completed = True
                        
                        else:
                            transaction_choice = int(transaction_choice)
                            if transaction_choice in range(1, len(self.my_unspent)+1):
                                transaction_choice_t = self.my_unspent[transaction_choice - 1]
                                if transaction_choice_t in transaction_to_spend:
                                    print('Please pick a transaction you have not already selected')
                                else:
                                    transaction_to_spend.append(transaction_choice_t)
                                    to_spend_value += transaction_choice_t.outputs[0].value
                                    print(transaction_to_spend)
                                    print(transaction_choice_t.to_json_complete())


            else:
                print('Not a valid choice')
                tried == False
                continue
            
            
            script_pub_key = input('Enter the public key of the desired recipient: ')

            if script_choice == "P2PKS":
                if self.check_addr(script_pub_key) == True:
                    pass
                else:
                    print('Secure key not valid')
                    continue

            script_pub_key = script_choice + ':' + script_pub_key
            
            value = None
            while value == None:
                value = int(input("Amount to spend (Transaction amount: "+str(to_spend_value) +"): "))
                if value < to_spend_value and value > 0:
                    transaction_fee = int(input("Transaction fee: "))
                    if transaction_fee > 0 and (transaction_fee + value) < to_spend_value:
                        tried = True
                        pass
                    else:
                        value = None
                        
                else:
                    value = None
                    print('incorrect value')
            # except:
            #     print('Incorrect details')
            #     tried = False
        
        return transaction_to_spend, script_pub_key, value, transaction_fee, to_spend_value

    def gen_coins(self):
        t = Transaction(None,[Transaction_Input("GENERATED_HASH", 'None')], [Transaction_Output("P2PK:" + self.pub_key_str, 100)], datetime.now(), 'GEN')
        self.last_transaction = t
        self.transaction_pool.add(t)
        prefixed_message="TRANSACTION:" + str(t.to_json_complete())
        self.transaction_messages.append(prefixed_message)
        self.send_message(prefixed_message)
        self.utxo()

    #### UTILITY FUNCTIONS ####

    def connect_to_peer(self, peer_port):
        peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_sock.connect(('127.0.0.1', peer_port))
        self.peers.append(peer_sock)
        self.peer_ports.append(peer_port)
        self.peer_dict[peer_sock] = peer_port
        message = "PORT:" + str(self.port) + '€'
        peer_sock.send(bytes(message, 'utf-8'))
        print(f'Connected to peer at port {peer_port}')

    def send_message(self, message):
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
        self.private_key = ECC.generate(curve='ed25519')
        self.public_key = self.private_key.public_key()
        self.pub_key_str = str(self.public_key.pointQ.x) + '+' + str(self.public_key.pointQ.y)


    def utxo(self):
        # list of all transactions in blockchain and transaction pool - genesis block
        all_transactions = self.blockchain.return_transactions() + self.transaction_pool.from_json_transactions()
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
                if self.check_addr(out_key_array[1]) == False:
                    print('Secure key not valid')
                output_key = self.addr_to_pub(out_key_array[1])

            if output_key == self.pub_key_str:
                my_unspent.append(transaction)
                balance += transaction.outputs[0].value
        

        self.unspent = unspent
        self.my_unspent = my_unspent
        self.balance = balance

    #### KEY SECURE FUNCTIONS 
    def pub_to_addr(self, key):
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
        addr_split= addr.split('+')

        check_string = addr_split[0] + '+' + addr_split[1] + '+'

        check_cs = sha256(check_string.encode('utf-8')).hexdigest()[:8]

        if check_cs == addr_split[2]:
            return True
        else:
            return False
    
    def addr_to_pub(self, addr):
        addr_array = addr.split('+')
        bytex = base58.b58decode(addr_array[0].encode('utf-8'))
        bytey = base58.b58decode(addr_array[1].encode('utf-8'))

        x= int.from_bytes(bytex, 'big')
        y= int.from_bytes(bytey, 'big')

        pub_key_str = str(x) + "+" +str(y)

        return pub_key_str


    def unspent_to_txt(self):
        try:
            os.remove('text/unspent_transactions.txt')
        except:
            pass
        self.utxo()
        file = open('text/unspent_transactions.txt', 'w')
        file.write('Unspent Transactions:')
        for i in range(len(self.my_unspent)):
            file.write('\n------------------------------------------------------------------------------\n')
            file.write('Transaction '+ str(i+1)+ ': \n')
            file.write(self.my_unspent[i].txt_format())

        file.close()
        os.system('open -t text/unspent_transactions.txt')