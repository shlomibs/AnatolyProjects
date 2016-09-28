#!/usr/bin/python
import random

def defaultPort():
	return random.randint(2048,65535) # 2**16-1
	#return 3846

def isPortTaken():
	raise Exception("Not implemented exception")

def startPortProtectionService(port):
	raise Exception("Not implemented exception")
