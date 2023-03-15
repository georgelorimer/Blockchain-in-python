
from Node import *

from tkinter import *

root = Tk()
frame = LabelFrame(root, text= "This is my frame", padx = 5, pady = 5)
frame.pack(padx=10, pady = 10)

e = Entry(frame)
e.pack()
e.insert(0, 'Enter your Port')

def final():
    my_port = e.get()
    peer_port = entry.get()
    p = Node(int(my_port),int(peer_port))
    frame.destroy()

def genesis():
    my_port = e.get()
    my_port_button1['state'] = DISABLED
    p = Node(int(my_port),None)
    frame.destroy()

def not_genesis():
    global entry
    my_port_button1(state=DISABLED)

    entry = Entry(frame)
    entry.pack()
    entry.insert(0, 'Enter the port to connect to')

    peer_port_button = Button(frame, text='Connect to no one', padx=50, pady=50, command=final)
    peer_port_button.pack()

    

def myclick():
    label = Label(root, text= e.get())
    label.pack()

my_port_button1 = Button(frame, text='Connect to no one', padx=50, pady=50, command=genesis)
my_port_button1.pack()

my_port_button2 = Button(frame, text='Connect to someone', padx=50, pady=50, command=not_genesis)
my_port_button2.pack()



root.mainloop()













# Handler
# TRANSACTION















