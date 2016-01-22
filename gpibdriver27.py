#!/usr/bin/env python
#gpib.py
#written by Kevin Ersoy in Python 2.7
import sys
import socket
import time
import visa

def connectGPIB(connectionString)
	my_instrument = visa.instrument(connectionString)
	return my_instrument
	
def queryGPIB(instrumentHandle, queryText):
	return instrumentHandle.ask(queryText)
	
def writeGPIB(instrumentHandle, writeText):
	instrumentHandle.write(writeText)
	return 1
	
def readGPIB(instrumentHandle):
	return instrumentHandle.read())