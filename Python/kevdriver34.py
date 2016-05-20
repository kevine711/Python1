#!/usr/bin/env python
#kevdriver.py
#written by Kevin Ersoy in Python 3
#connect_IP_Port returns a socket
#write_Socket_Text returns 1
#read_Socket returns an array of text lines
#disconnect_Socket returns 1
import socket
import time
import sys

def connect_IP_Port(IP, Port): #returns a socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((IP, Port))
	return s

def write_Socket_Text(Socket, Text): #returns nothing
	Socket.send(Text.encode())
	
def read_Socket(Socket):
	data = Socket.recv(2048)
	print (data.decode('ascii'))
