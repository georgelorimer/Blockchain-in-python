from tkinter import *
from Node import Node


class Gui:

    def __init__(self) -> None:
        self.open_frame = None

        self.root = Tk()
        self.root.title("Greckle Wallet")
        self.menu_buttons = []

        self.home = Button(self.root, text='Home', state=DISABLED, command=self.home_op)
        self.menu_buttons.append(self.home)

        self.transactions = Button(self.root, text='Transactions', state=DISABLED)
        self.menu_buttons.append(self.transactions)

        self.block_explorer = Button(self.root, text='Block Explorer', state=DISABLED)
        self.menu_buttons.append(self.block_explorer)

        self.attacks = Button(self.root, text='Attacks', state=DISABLED)
        self.menu_buttons.append(self.attacks)

        self.other = Button(self.root, text='Other', state=DISABLED)
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
        self.login_frame.grid(row=1, column= 0,columnspan=6, padx=10, pady = 10)

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
        self.home_op()


    #### HOME FRAME ####

    def home_op(self):
        self.delete_frame()

        self.home_frame = LabelFrame(self.root)
        self.home_frame.grid(row=1, column= 0,columnspan=6, padx=10, pady = 10)

        self.open_frame = self.home_frame

        port_lable = Label(self.home_frame, text='Port Number:')
        port_lable.grid(row=0, column=0)
        port_out = Label(self.home_frame, text= self.node.port)
        port_out.grid(row=0, column=1)

        peers_lable = Label(self.home_frame, text='Peer ports')
        peers_lable.grid(row=3, column=0)
        peers_out = Label(self.home_frame, text= self.node.peer_ports)
        peers_out.grid(row=3, column=1)

        pk_lable = Label(self.home_frame, text='Public Key:')
        pk_lable.grid(row=1, column=0)
        pk_out = Text(self.home_frame, width= 50, height=4)
        pk_out.insert(1.0, self.node.pub_key_str)
        pk_out.grid(row=1, column=1)

        pks_lable = Label(self.home_frame, text='Secure Public Key:')
        pks_lable.grid(row=2, column=0)
        pks_out = Text(self.home_frame, width=50, height=2)
        pks_out.insert(1.0, self.node.pub_to_addr(self.node.pub_key_str))
        pks_out.grid(row=2, column=1)

        opt_label = Label(self.home_frame, text='Mining:')
        opt_label.grid(row=4, column=0)

        if self.node.mining == True:
            btn_text = 'ON'
        elif self.node.eligible == False:
            btn_text = 'OFF'
        
        self.opt_but = Button(self.home_frame, text=btn_text, width= 2)
        if self.node.eligible == False:
            self.opt_but['state'] = DISABLED
        self.opt_but['command'] = lambda: self.flip_opt(self.opt_but, None)
        self.opt_but.grid(row=4, column=1)





    #### UTLITY FUNCTIONS ####

    def delete_frame(self):
        for button in self.menu_buttons:
            button['state'] = NORMAL
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
        elif button['text'] == 'OFF':
            button['text'] = 'ON'


Gui()