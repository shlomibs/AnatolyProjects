#!/usr/bin/python
import random
import psutil
import netifaces
import urllib

def defaultCommunicationKey():
	return 101545212242583985165441321575825841448539185773823062345343881943249369033766213167519885694700152054979752683388685684463697625837051689386181570147819986261585555456775184136111651197615518323889751215176413141310764435890247842293816357912848606746000981945465934096637352676816034266960374526253061445872L # 1024 bit random val

def defaultPort():
	return random.randint(2048,65535) # 2**16-1
	#return 3846

def isPortTaken(port): # FIN
	return port in [i.laddr[1] for i in psutil.net_connections()]

def getDirServerAddr(): # FIN
	try:
		# dirServers = urllib.urlopen("http://dirser.honor.es/dirSer/status.php").read().split("\n")[1:]
		dirServers = urllib.urlopen("http://dirser.atwebpages.com/dirSer/status.php").read().split("\n")[1:]
		#print "dir servers: " + str(dirServers)
		addr = dirServers[random.randint(0, len(dirServers) - 1)].split(",") # getting random server
		# change to get from all
		addr[1] = int(addr[1]) # port to integer
		return tuple(addr[0:2]) # [0:2] for future developments like adding ID's and more
	except: # Exception as e:
		#print e
		raise Exception("could not get directory server addr")

# returns the IPv4 addresses
def GetMachineInternalIps(): # its a generator
	for interface in netifaces.interfaces():
		try:
			for link in netifaces.ifaddresses(interface)[netifaces.AF_INET]:
				yield link['addr']
		except: # no IPv4 address
			pass