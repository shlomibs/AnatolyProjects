#!/usr/bin/python
import random
import psutil
import netifaces

def defaultPort():
	return random.randint(2048,65535) # 2**16-1
	#return 3846

def isPortTaken(port): # FIN
	return port in [i.laddr[1] for i in psutil.net_connections()]

def getDirServerAddr(): # FIN
	try:
		dirServers = urllib.urlopen("http://dirser.honor.es/dirSer/status.php").read().split("\n")[1:]
		addr = dirServers[random.randint(0, len(dirServers))].split(",") # getting random server
		# change to get from all
		addr[1] = int(addr[1]) # port to integer
		return tuple(addr[0:2]) # [0:2] for future developments like adding ID's and more
	except: # Exception as e:
		raise Exception("could not get directory server addr")

def GetMachineInternalIps(): # its a generator !!
	for interface in netifaces.interfaces():
		for link in netifaces.ifaddresses(interface)[netifaces.AF_INET]:
			yield link['addr']