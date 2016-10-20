#!/usr/bin/python
import random
import psutil

def defaultPort():
	return random.randint(2048,65535) # 2**16-1
	#return 3846

def isPortTaken(port): # FIN
	return port in [i.laddr[1] for i in psutil.net_connections()]
