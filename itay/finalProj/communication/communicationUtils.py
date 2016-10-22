#!/usr/bin/python
import random
import psutil

def defaultPort():
	return random.randint(2048,65535) # 2**16-1
	#return 3846

def isPortTaken(port): # FIN
	return port in [i.laddr[1] for i in psutil.net_connections()]

def getDirServerAddr():
	dirServers = urllib.urlopen("http://dirser.honor.es/dirSer/status.php").read().split("\n")[1:]
	return tuple(dirServers[random.randint(0, len(dirServers))].split(",")) # getting random server
