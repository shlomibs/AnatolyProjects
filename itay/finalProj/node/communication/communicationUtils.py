#!/usr/bin/python
import random
import psutil

def defaultPort():
	return random.randint(2048,65535) # 2**16-1
	#return 3846

def isPortTaken(port): # FIN
	return port in [i.laddr[1] for i in psutil.net_connections()]

def getDirServerAddr(): # FIN
	dirServers = urllib.urlopen("http://dirser.honor.es/dirSer/status.php").read().split("\n")[1:]
	addr = dirServers[random.randint(0, len(dirServers))].split(",") # getting random server
	addr[1] = int(addr[1]) # port to integer
	return tuple(addr[0:2]) # [0:2] for future developments like adding ID's and more
