#!/usr/bin/env python
#testclient.py
#written by Kevin Ersoy in Python 3
import socket
import time
import sys
sys.path.append("C:\python") #add path to kevdriver to sys.path
import kevdriver

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = kevdriver.connect_IP_Port('termserv-ip', 23)
s.recv(2048)
kevdriver.write_Socket_Text(s, 'cisco\n')
#kevdriver.read_Socket(s)
kevdriver.write_Socket_Text(s, 'enable\n')
#kevdriver.read_Socket(s)
kevdriver.write_Socket_Text(s, 'cisco\n')
#kevdriver.read_Socket(s)
kevdriver.write_Socket_Text(s, 'clear line 3\n')
kevdriver.write_Socket_Text(s, '\n')
kevdriver.read_Socket(s)
kevdriver.read_Socket(s)
time.sleep(0.25)
kevdriver.read_Socket(s)
time.sleep(0.25)
s.close()
