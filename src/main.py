from tkinter import *
from tkinter import ttk
from datetime import datetime

from Node import Node



class Gui:

    def __init__(self) -> None:
        self.open_frame = None

        self.root = Tk()
        self.root.geometry('550x300')
        self.root.rowconfigure(1,weight=50)
        self.root.title("Greckle Wallet")
        self.menu_buttons = []

        self.home = Button(self.root, text='Home', state=DISABLED, command=self.home_op)
        self.menu_buttons.append(self.home)

        self.transactions = Button(self.root, text='Transactions', state=DISABLED, command=self.transaction_op)
        self.menu_buttons.append(self.transactions)

        self.block_explorer = Button(self.root, text='Block Explorer', state=DISABLED, command=self.be_op)
        self.menu_buttons.append(self.block_explorer)

        self.attacks = Button(self.root, text='Attacks', state=DISABLED)
        self.menu_buttons.append(self.attacks)

        self.other = Button(self.root, text='Other', state=DISABLED, command=self.other_op)
        self.menu_buttons.append(self.other)

        self.manual = Button(self.root, text='Manual', state=DISABLED)
        self.menu_buttons.append(self.manual)

        self.home.grid(row=0, column=0)
        self.transactions.grid(row=0, column=1)
        self.block_explorer.grid(row=0, column=2)
        self.attacks.grid(row=0, column=3)
        self.other.grid(row=0, column=4)
        self.manual.grid(row=0, column=5)

        self.enter()



        self.root.mainloop()

    #### CONNECT FRAME ####

    def enter(self):
        self.login_frame = LabelFrame(self.root, text = 'Connect')
        self.login_frame.grid(row=1, column= 0,columnspan=6)

        self.open_frame = self.login_frame

        port_lable = Label(self.login_frame, text='Your Port Number:')
        port_lable.grid(row=0, column=0)
        self.port_input = Entry(self.login_frame, width=5)
        self.port_input.grid(row=0, column=1)

        conn_lable = Label(self.login_frame, text='Peer Port Number:')
        conn_lable.grid(row=2, column=0)
        self.conn_input = Entry(self.login_frame, width=5, state=DISABLED)
        self.conn_input.grid(row=2, column=1)


        opt_label = Label(self.login_frame, text='Connect to a port:')
        opt_label.grid(row=1, column=0)
        self.opt_but = Button(self.login_frame, text='NO', width= 2)
        self.opt_but['command'] = lambda: self.flip_opt(self.opt_but, self.conn_input)
        self.opt_but.grid(row=1, column=1)

        connect = Button(self.login_frame, text='Connect', command= self.start)
        connect.grid(row=3, column=0, columnspan=2)

        

        # self.b = Button(self.login_frame, text='delete frame', command=self.delete_frame(self.login_frame))
        # self.b.grid(row=3, column=2)

    def start(self):
        port = self.port_input.get()
        if self.opt_but['text'] == "YES":
            peer = int(self.conn_input.get())
        elif self.opt_but['text'] == "NO":
            peer = None
        
        self.node = Node(int(port),peer)

        self.main_frame_open()
        self.home_op()


    #### MAIN FRAME ####
    def main_frame_open(self):
        self.main_frame = Frame(self.root, pady=10, padx=10)
        self.main_frame.grid(row=1, columnspan=6, sticky= 'nsew')
        self.main_canvas = Canvas(self.main_frame)
        self.main_canvas.pack(side=LEFT, fill= BOTH, expand=1)

        self.main_scrollbar = ttk.Scrollbar(self.main_frame, orient=VERTICAL, command=self.main_canvas.yview)
        self.main_scrollbar.pack(side=RIGHT, fill=Y)

        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        self.main_canvas.bind('<Configure>', lambda e: self.main_canvas.configure(scrollregion= self.main_canvas.bbox("all")))

        self.second_frame = Frame(self.main_canvas)
        self.main_canvas.create_window((0,0), window=self.second_frame, anchor=N)




    #### HOME FRAME ####

    def home_op(self):
        self.node.utxo()
        self.delete_frame()

        self.home_frame = Frame(self.second_frame, pady=10)
        self.home_frame.pack(fill= BOTH, expand = 1, side=TOP)

        self.open_frame = self.home_frame

        port_lable = Label(self.home_frame, text='Port Number:')
        port_lable.grid(row=0, column=0)
        port_out = Label(self.home_frame, text= self.node.port)
        port_out.grid(row=0, column=1)

        acount_balance = Label(self.home_frame, text='Acount Balance:')
        acount_balance.grid(row=1, column=0)
        acount_balance_out = Label(self.home_frame, text= self.node.balance)
        acount_balance_out.grid(row=1, column=1)

        peers_lable = Label(self.home_frame, text='Peer ports:')
        peers_lable.grid(row=4, column=0)
        peers_out = Label(self.home_frame, text= self.node.peer_ports)
        peers_out.grid(row=4, column=1)

        pk_lable = Label(self.home_frame, text='Public Key:')
        pk_lable.grid(row=2, column=0)
        pk_out = Text(self.home_frame, width= 50, height=4)
        pk_out.insert(1.0, self.node.pub_key_str)
        pk_out.grid(row=2, column=1)

        pks_lable = Label(self.home_frame, text='Secure Public Key:')
        pks_lable.grid(row=3, column=0)
        pks_out = Text(self.home_frame, width=50, height=2)
        pks_out.insert(1.0, self.node.pub_to_addr(self.node.pub_key_str))
        pks_out.grid(row=3, column=1)

        opt_label = Label(self.home_frame, text='Mining:')
        opt_label.grid(row=5, column=0)

        if self.node.mining == True:
            btn_text = 'ON'
        elif self.node.mining == False:
            btn_text = 'OFF'
        
        if self.node.eligible == True: 
            self.opt_but = Button(self.home_frame, text=btn_text, width= 2)
            self.opt_but['command'] = lambda: self.flip_opt(self.opt_but, None)
            self.opt_but.grid(row=5, column=1)

        elif self.node.eligible == False:
            port_out = Label(self.home_frame, text= 'Please wait until the next round to interact with the network')
            port_out.grid(row=5, column=1)

        time_lable = Label(self.home_frame, text='Time until next round:')
        time_lable.grid(row=6, column=0)
        time_out = Label(self.home_frame, text= self.node.time_for_next_round - datetime.now())
        time_out.grid(row=6, column=1)
        

    #### TRANSACTION FRAME ####

    def transaction_op(self):
        self.delete_frame()

        self.transaction_frame = Frame(self.second_frame, pady=10)
        self.transaction_frame.pack(fill= BOTH, expand = 1, side=TOP)

        self.open_frame = self.transaction_frame

        acount_balance = Label(self.transaction_frame, text='Acount Balance:', padx=40, pady=10)
        acount_balance.grid(row=0, column=1)
        acount_balance_out = Label(self.transaction_frame, text= self.node.balance, padx=40, pady=10)
        acount_balance_out.grid(row=0, column=2)

        p1 = Label(self.transaction_frame, text='      ')
        p1.grid(row=0, column=3)

        unspent_btn = Button(self.transaction_frame, text= 'Unspent transactions', command=self.node.unspent_to_txt)
        unspent_btn.grid(row=1, column=1)

        unspent_btn = Button(self.transaction_frame, text= 'Create a transaction', command=self.c_transaction_op)
        unspent_btn.grid(row=1, column=2)

        lt_lable = Label(self.transaction_frame, text='Last Transaction:', padx=10, pady=10)
        lt_lable.grid(row=2, column=0)
        if self.node.last_transaction != None:
            lt_out = Label(self.transaction_frame, text= self.node.last_transaction.hash[:40] + '...')
            lt_out.grid(row=2, column=1, columnspan=3)

            val = Label(self.transaction_frame, text='Value:')
            val_out = Label(self.transaction_frame, text= self.node.last_transaction.outputs[0].value)
            val.grid(row=3, column=0)
            val_out.grid(row=3, column=1, columnspan=3)

            tim = Label(self.transaction_frame, text='Time Stamp:')
            tim_out = Label(self.transaction_frame, text= self.node.last_transaction.timestamp)
            tim.grid(row=4, column=0)
            tim_out.grid(row=4, column=1, columnspan=3)
            
            type = Label(self.transaction_frame, text='Type:')
            type_out = Label(self.transaction_frame, text= self.node.last_transaction.type)
            type.grid(row=5, column=0)
            type_out.grid(row=5, column=1, columnspan=3)
            
            view_transaction = Button(self.transaction_frame, text= 'View Transaction', command= self.node.last_transaction.to_txt)
            view_transaction.grid(row=6, column=2, sticky=E)


    #### CREATE TRANSACTIONS ####

    def c_transaction_op(self):
        self.node.utxo()
        self.my_unspent = self.node.my_unspent.copy()
        self.to_spend_value = 0
        self.transactions_to_send = []

        self.delete_frame()

        self.c_transaction_frame = Frame(self.second_frame)
        self.c_transaction_frame.pack(fill= BOTH, expand = 1, anchor=N)

        self.open_frame = self.c_transaction_frame
        
        choice_label = Label(self.c_transaction_frame, text='Scripting Option:')
        choice_label.grid(row=0, column=0)
        self.choice = Button(self.c_transaction_frame, text= 'P2PK', command=self.flip_choice)
        self.choice.grid(row=0, column=1, columnspan=2)
        self.info = Label(self.c_transaction_frame,  text='Send to public key')
        self.info.grid(row=1, column=0, columnspan=3)

        self.unspent_label = Label(self.c_transaction_frame, text='Please select a transaction:')
        self.unspent_label.grid(row=2, column=0)

        unspent_btn = Button(self.c_transaction_frame, text= 'Inspect unspent transactions', command=self.node.unspent_to_txt)
        unspent_btn.grid(row=2, column=1, columnspan=2)

        self.amount_label = Label(self.c_transaction_frame, text='Amount To spend: '+ str(self.to_spend_value))
        self.amount_label.grid(row=3, column=0)
        
        restart_button = Button(self.c_transaction_frame, text = 'Restart', command=self.c_transaction_op)
        restart_button.grid(row=3, column=1, sticky=W)
        
        confirm_button = Button(self.c_transaction_frame, text = 'Confirm', command=lambda: self.d_transaction_op(self.choice['text']))
        confirm_button.grid(row=3, column=2, sticky=W)


        self.t_btns = []
        my_unspent = self.node.my_unspent.copy()
        for i in range(len(my_unspent)):
            
            t_btn = Button(self.c_transaction_frame, text = 'Hash: '+my_unspent[i].hash[:40] + '...| Value: '+ str(my_unspent[i].outputs[0].value), width=50, command= lambda i=i: self.select_transaction(i))
            t_btn.grid(row=4+i, column=0, columnspan= 3)
            self.t_btns.append(t_btn)
        
    #### DETAILS FRAME ####
    def d_transaction_op(self, choice):
        self.delete_frame()
        self.choice = choice
        self.d_transaction_frame = Frame(self.second_frame)
        self.d_transaction_frame.pack(fill= BOTH, expand = 1, anchor=N)

        self.open_frame = self.d_transaction_frame

        to_spend_lbl = Label(self.d_transaction_frame, text='Amount to spend: '+str(self.to_spend_value))


        val_lbl = Label(self.d_transaction_frame, text = 'Enter amount to send:')
        val_entr = Entry(self.d_transaction_frame)

        fee_lbl = Label(self.d_transaction_frame, text = 'Enter transaction fee or leave empty:')
        fee_entr = Entry(self.d_transaction_frame)

        addr_lbl = Label(self.d_transaction_frame, text = 'Recipient address:')
        addr_entr = Entry(self.d_transaction_frame)

        to_spend_lbl.grid(row=0, column=0, columnspan=3)
        val_lbl.grid(row=1, column=0)
        val_entr.grid(row=1, column=1, columnspan=2, sticky=E)
        fee_lbl.grid(row=2, column=0, columnspan= 2, sticky= W)
        fee_entr.grid(row=2, column=2, sticky=E)
        addr_lbl.grid(row=3, column=0)
        addr_entr.grid(row=3, column=1, columnspan=2)

        clear_button = Button(self.d_transaction_frame, text='Clear', command=self.d_transaction_op)
        confirm_button = Button(self.d_transaction_frame, text='Confirm', command= lambda: self.transaction_details(addr_entr.get(), val_entr.get(), fee_entr.get()))

        clear_button.grid(row=4, column=1)
        confirm_button.grid(row=4, column=2)


    #### BLOCK EXPLORER FRAME ###
    def be_op(self):
        self.root.geometry('550x300')
        self.delete_frame()
        self.be_frame = Frame(self.second_frame)
        self.be_frame.pack(fill= BOTH, expand = 1, anchor=N)

        self.open_frame = self.be_frame

        self.blockchain = self.node.blockchain.blockchain.copy()
        self.blockchain.reverse()

        Label(self.be_frame, text= 'Blockchain Explorer').pack()

        self.b_btns = []
        
        for i in range(len(self.blockchain)):
            if i != 0:
                Label(self.be_frame, text='^').pack()
            dt =  self.blockchain[i].time
            time = str(dt[2]) + '/' + str(dt[1]) + '/' + str(dt[0]) + '-' + str(dt[3]) + ':' + str(dt[4]) +':'+ str(dt[5])
            b_btn = Button(self.be_frame, text = 'Hash: '+self.blockchain[i].block_hash[:20] + '...| Time Stamp: '+ time, width=50, command= lambda i=i: self.select_block(i))
            b_btn.pack()
            self.b_btns.append(b_btn)



    #### OTHER FRAME ####
    def other_op(self):
        self.delete_frame()

        self.other_frame = Frame(self.second_frame, pady=10)
        self.other_frame.pack(fill= BOTH, expand = 1)

        self.open_frame = self.other_frame

        gen = Button(self.other_frame, text= 'Generate Coins', command= self.node.gen_coins)
        gen.pack()




    #### UTLITY FUNCTIONS ####

    def delete_frame(self):
        for button in self.menu_buttons:
            button['state'] = NORMAL
        if self.node.eligible == False:
            self.transactions['state'] = DISABLED
            self.attacks['state'] = DISABLED
        self.open_frame.destroy()

    def flip_opt(self, button, widg):
        if button['text'] == 'NO':
            widg['state'] = NORMAL
            button['text'] = 'YES'
        elif button['text'] == 'YES':
            widg['state'] = DISABLED
            button['text'] = 'NO'

        elif button['text'] == 'ON':
            button['text'] = 'OFF'
            self.node.mining = False
        elif button['text'] == 'OFF':
            button['text'] = 'ON'
            self.node.mining = True
    
    def flip_choice(self):
        for b in self.t_btns:
            b['state'] = NORMAL
        self.to_spend_value = 0
        self.amount_label['text'] = 'Amount To spend: '+ str(self.to_spend_value)
        if self.choice['text'] == 'P2PK':
            self.choice['text'] = 'P2PKS'
            self.unspent_label['text'] = 'Please select a transaction:'
            self.info['text'] = 'Send to secure public key'
            self.transactions_to_send = []
        elif self.choice['text'] == 'P2PKS':
            self.choice['text'] = 'MULTIP2PK'
            self.info['text'] = 'Send multiple transactions to public key'
            self.unspent_label['text'] = 'Select transaction multiple transaction:'
            self.transactions_to_send = []
        elif self.choice['text'] == 'MULTIP2PK':
            self.choice['text'] = 'P2PK'
            self.info['text'] = 'Send to public key'
            self.unspent_label['text'] = 'Please select a transaction:'
            self.transactions_to_send = []

    def select_transaction(self, i):
        if self.choice['text'] == 'P2PK' or self.choice['text'] == 'P2PKS':
            for btn in self.t_btns:
                if btn['state'] == DISABLED:
                    btn['state'] = NORMAL
            self.transactions_to_send = [self.my_unspent[i]]
            self.t_btns[i]['state'] = DISABLED
            self.to_spend_value = self.my_unspent[i].outputs[0].value
            self.amount_label['text'] = 'Amount To spend: '+ str(self.to_spend_value)
            # next page
        elif self.choice['text'] == 'MULTIP2PK':
            self.transactions_to_send.append(self.my_unspent[i])
            self.t_btns[i]['state'] = DISABLED
            self.to_spend_value += self.my_unspent[i].outputs[0].value
            self.amount_label['text'] = 'Amount To spend: '+ str(self.to_spend_value)

    def select_block(self, i):
        block = self.blockchain[i]


        self.delete_frame()

        self.block_frame = Frame(self.second_frame, pady=10)
        self.block_frame.pack(fill= BOTH, expand = 1)

        self.open_frame = self.block_frame

        h_lbl = Label(self.block_frame, text= 'Hash:')
        h_lbl.grid(row=0, column=0)
        h_out = Label(self.block_frame, text= block.block_hash[:40] + '...')
        h_out.grid(row=0, column=1)

        ph = Label(self.block_frame, text='Previous Hash:')
        try:
            ph_out = Label(self.block_frame, text= block.prev_block_hash[:30]+ '...')
        except:
            ph_out = Label(self.block_frame, text= 'None')
        ph.grid(row=1, column=0)
        ph_out.grid(row=1, column=1)

        tim = Label(self.block_frame, text='Time Stamp:')
        tim_out = Label(self.block_frame, text= block.time)
        tim.grid(row=2, column=0)
        tim_out.grid(row=2, column=1)
        
        non = Label(self.block_frame, text='Nonce:')
        non_out = Label(self.block_frame, text= block.nonce)
        non.grid(row=3, column=0)
        non_out.grid(row=3, column=1)

        cb = Label(self.block_frame, text='Coinbase Fee:')
        if block.block_hash == 'GENESIS_HASH':
            cb_out = Label(self.block_frame, text= 'None')
        else:
            cb_out = Label(self.block_frame, text= '50')
        cb.grid(row=4, column=0)
        cb_out.grid(row=4, column=1)

        
        tf = Label(self.block_frame, text='Transaction Fee:')
        try:
            tf_out = Label(self.block_frame, text= block.block_transactions[0].outputs[0].value - 50)
        except:
            tf_out = Label(self.block_frame, text= 'None')
        tf.grid(row=5, column=0)
        tf_out.grid(row=5, column=1)

        view = Button(self.block_frame, text= 'Block Transactions', command= block.to_txt)
        back = Button(self.block_frame, text= 'Back', command= self.be_op)
        view.grid(row=6, column=0)
        back.grid(row=6, column=1)
        if block.block_hash == 'GENESIS_HASH':
            view['state'] = DISABLED
        


    def transaction_details(self, script_public_key, value, transaction_fee):
        success = self.node.transaction_maker(self.transactions_to_send, str(self.choice+':'+script_public_key), int(value), int(transaction_fee), int(self.to_spend_value))
        self.delete_frame()
        self.success_frame = Frame(self.second_frame, pady=10)
        self.success_frame.pack(fill= BOTH, expand = 1)

        self.open_frame = self.success_frame

        if success == True:
            message = 'Transaction Succesful, you sent '+value+' Greckles!'
        else:
            message = 'Something went wrong, please try again.'
        
        Label(self.success_frame, text=message).pack()

        Button(self.success_frame, text='Continue', command=self.home_op).pack()


Gui()