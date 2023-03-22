import sys
import subprocess

subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'pycryptodome'])

subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'base58'])