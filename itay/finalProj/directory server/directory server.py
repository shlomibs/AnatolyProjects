#!/usr/bin/python
from uploadToDirSer import upload
from socket import *
import urllib
from thread import start_new_thread
from time import time, sleep

class Server: # FIN
	def __init__(self):
		self.port = 13013
		self.s = socket(AF_INET, SOCK_DGRAM)
		self.s.bind(("0.0.0.0", self.port))
		self.isShutdown = False
		self.clients = [] # (ID, address)
		self.clientsLastCommunication = {} # class
		self.MAX_NODES_NUM_TO_SEND = 20 # to fit to one packet
		self.CLIENT_TIMEOUT = 3 * 4
		self.SERVER = "dirser.atwebpages.com"
		self.EOM = "<EOF>" # end of message

	def uploadAddr(self): # FIN
		# get current status
		upToDateStatus = urllib.urlopen("http://" + self.SERVER + "/dirSer/status.php").read().replace("\r", "") # turn \r\n to \n
		# edit status file
		f = open("upload/status.php", "w")
		f.write(upToDateStatus + "\n" + self.getMyIp() + "," + str(self.port))
		f.close()
		# then upload status
		if not upload(True): #True): # upload and not verbose
			for i in range(2): # try 2 more times
				if upload(True): # break
					break
				if i == 1: # third try failed
					return False #raise Exception("upload failed")
		return True

	def start(self): # FIN
		if not self.uploadAddr(): # upload the address
			return False # fail
		start_new_thread(self.run, ()) # then start the server
		return True # success

	def run(self): # FIN
		start_new_thread(self.checkConnectionThread, ())
		#start_new_thread(self.recvThread, ())
		self.recvThread()

	def recvThread(self): # FIN
		while not self.isShutdown:
			data, addr = self.s.recvfrom(1024) # data = ID
			#splt = data.split(",")
			#if ">" in data: # want nodes list data = [ID]>[node type] # => data.split(">") = [ID, node type]
			print "input data: " + data + " \nfrom: " + str(addr)
			if data[0] == ">": # request for nodes list
				# can be also regular notification (usually hole punching) -> that's what the if is for
				contacts = self.getContacts(data[1:])
				print "sending contacts: " +str(contacts) + " to: " + data[1:]
				contacts = [contacts[i:i + 10] for i in xrange(0, len(contacts), 10)] # split to force it to send each list in the same packet
				for i in xrange(len(contacts)):
					self.s.sendTo("0," + str(i) + ",m," + repr(contacts[i]), addr) # directory servers ID's are all 0
				#self.s.sendTo("0," + len(contacts) + ",m," + self.EOM, addr) # 1 = next seq
			# regular notification (usually hole punching)
			data = data.replace(">", "")
			if (data, addr) not in self.clients:
				self.clients.append((data, addr)) # ID, ADDR
			self.clientsLastCommunication[(data, addr)] = time()

	def checkConnectionThread(self): # FIN
		while not self.isShutdown:
			i=0
			while i < len(self.clients):
				if time() - self.clientsLastCommunication[self.clients[i]] > self.CLIENT_TIMEOUT: # remove if connection timed out
					del self.clientsLastCommunication[self.clients[i]]
					self.clients.remove(self.clients[i])
				else:
					i += 1
			sleep(0.2)

	def getMyIp(self): # external ip # FIN
		checkIpSock = socket(AF_INET, SOCK_DGRAM)
		checkIpSock.connect(('8.8.8.8', 0)) # connecting to a UDP address doesn't send packets
		return checkIpSock.getsockname()[0]

	def getContacts(self, ID): # FIN
		# send list of ID's and addresses of nodes that this node[ID] can send to
		return [c for c in self.clients if c is not ID]

	def shutdown(self): # FIN
		self.isShutdown = True
		upToDateStatus = urllib.urlopen("http://" + self.SERVER + "/dirSer/status.php").read()
		upToDateStatus = upToDateStatus.replace("\n" + self.getMyIp() + "," + str(self.port), "") # remove this addr
		f = open("upload/status.php", "w")
		f.write(upToDateStatus)
		f.close()
		if not upload(True): # upload and not verbose
			for i in range(2): # try 2 more times
				if upload(True): # break
					break
				if i == 1:
					raise Exception("upload failed")
		sleep(0.5)



def main(): # FIN
	# upload external address and port ..
	server = Server()
	if not server.start():
		print "failure!\n exiting . . ."
		return
	print ">> started port: " + str(server.port) + " . . ."
	cmds = ["shutdown", "exit", "close", "quit"]
	while True:
		inp = raw_input(">> ")
		if inp.lower() in cmds: # to lower case
			print "shutting down . . ."
			server.shutdown()
			break
		else:
			print "illegal command, available commands: " + ", ".join(cmds)
			print "clients: " + str(server.clients)
		

if __name__ == "__main__":
	main()



