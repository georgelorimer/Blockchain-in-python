# Greckle

This project is a new blockchain cryptocurrency called Greckle.

The project consists of a P2P network, Transaction Layer, Block explorer and wallet GUI for you to use the system.

The code should run on all python3 instances and most of python2. However, if you come into any issues, please change your python version to 3.9.10 as this is the version the project was created and tested in.

When you run the program, external files will automatically be installed with pip. Please make sure you have pip installed.

Once you have used the code, if you wish to uninstall the libraries please use the following commands:

pip uninstall pycryptodome
pip uninstall base58

To run the code open a terminal and go to the parent directory “Greckle” and use the command:

python src/main.py

To open multiple nodes run this command in different terminals which will open different wallet GUIs. These will be the different nodes in the system.

When you run the command the tkinter GUI will open. Click on the “Manual” tab in the menu bar to open “Greckle_Manual.pdf” (this can also be found at the location Greckle/text/Greckle_Manual.pdf). Read through the manual completely to learn how to use the system and follow the instructions on how to connect a node to a port number.

All the information to use the system is in the manual apart from one thing:
If you try and enter the system with a port number that is already in use or you try to connect to a port that doesn’t exist the GUI will exit. This is because when it has tried to connect and fails, ports have been opened that are not used by the code. If this happens a “Port error” message will be shown in the terminal and these ports will be closed. If this happens simply rerun the command in the terminal and use the correct port numbers described in the manual.

Another thing to note is you need to also exit the code with the “Exit” button in the menu bar as this exits the code correctly.

The documentation can be viewed through the path:
Greckle/Greckle_Documentation/docs/_build/html/

Once in the folder open index.html with your browser.

That’s everything. If you have any questions or problems please email:
george.lorimer@student.manchester.ac.uk

I hope you enjoy using Greckle.
