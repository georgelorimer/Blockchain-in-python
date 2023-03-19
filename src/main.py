from tkinter import *

class Gui:

    def __init__(self) -> None:
        self.root = Tk()
        self.root.title("Greckle Wallet")
        self.menu_buttons = []

        self.home = Button(self.root, text='Home', state=DISABLED)
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



    def enter(self):
        self.login_frame = LabelFrame(self.root, text = 'Connect')
        self.login_frame.grid(row=1, column= 0,columnspan=6, padx=10, pady = 10)

        self.port_lable = Label(self.login_frame, text='Your Port Number:')
        self.port_lable.grid(row=0, column=0)
        self.port_input = Entry(self.login_frame, width=5)
        self.port_input.grid(row=0, column=1)

        self.conn_lable = Label(self.login_frame, text='Peer Port Number:')
        self.conn_lable.grid(row=2, column=0)
        self.conn_input = Entry(self.login_frame, width=5, state=DISABLED)
        self.conn_input.grid(row=2, column=1)


        self.opt_label = Label(self.login_frame, text='Connect to a port:')
        self.opt_label.grid(row=1, column=0)
        self.opt_but = Button(self.login_frame, text='NO', width= 2)
        self.opt_but['command'] = lambda: self.flip_opt(self.opt_but, self.conn_input)
        self.opt_but.grid(row=1, column=1)

        connect = Button(self.login_frame, text='Connect', command=lambda: self.start(self.login_frame))
        connect.grid(row=3, column=0, columnspan=2)

        

        # self.b = Button(self.login_frame, text='delete frame', command=self.delete_frame(self.login_frame))
        # self.b.grid(row=3, column=2)

    def start(self, frame):
        port = self.port_input.get()
        if self.opt_but['text'] == "YES":
            peer = self.conn_input.get()
        elif self.opt_but['text'] == "NO":
            peer = None

        self.delete_frame(frame)

    def delete_frame(self, frame):
        for button in self.menu_buttons:
            button['state'] = NORMAL
        frame.destroy()

    def flip_opt(self, button, widg):
        if button['text'] == 'NO':
            widg['state'] = NORMAL
            button['text'] = 'YES'
        elif button['text'] == 'YES':
            widg['state'] = DISABLED
            button['text'] = 'NO'


Gui()