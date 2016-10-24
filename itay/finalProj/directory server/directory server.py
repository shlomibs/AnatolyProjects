from uploadToDirSer import upload
from socket import *
from thread import start_new_thread
from time import time

class Server:
	def __init__(self):
		self.port = 13013
		self.s = socket(AF_INET, SOCK_DGRAM)
		self.s.bind(("0.0.0.0", self.port))
		self.uploadAddr()
		self.isShutdown = False
		self.clients = [] # (ID, address)
		self.clientsLastCommunication = {} # class
		self.MAX_NODES_NUM = 20 # to fit to one packet
		self.CLIENT_TIMEOUT = 3 * 4

	def uploadAddr(self): # FIN
		# get current status
		upToDateStatus = urllib.urlopen("http://dirser.honor.es/dirSer/status.php").read().replace("\r", "") # turn \r\n to \n
		# edit status file
		f = open("upload/status.php", "w")
		f.write(upToDateStatus + "\n" + self.getMyIp() + "," + str(self.port))
		f.close()
		# then upload status
		if !upload(True): # upload and not verbose
			for i in range(2): # try 2 more times
				if upload(True): # break
					break
				if i == 1:
					raise Exception("upload failed")

	def start(self): # FIN
		start_new_thread(self.run, ())

	def run(self): # FIN
		start_new_thread(self.checkConnectionThread, ())
		#start_new_thread(self.recvThread, ())
		self.recvThread()

	def recvThread(self): # FIN
		while !self.Shutdown:
			data, addr = self.s.recvfrom(1024) # data = ID
			#if ">" in data: # want nodes list data = [ID]>[node type] # => data.split(">") = [ID, node type]
			if data[-1] == ">" # request for nodes list
				self.s.sendTo(self.getContacts(data[:-1], addr)
			else: # regular notification (usually hole punching)
				if (data,addr) not in self.clients:
					self.clients.append((data, addr))
				self.clientsLastCommunication[(data, addr)] = time()

	def checkConnectionThread(): # FIN
		while !self.shutdown:
			i=0
			while i < len(self.clients):
				if time() - self.clientsLastCommunication[self.clients[i]] > self.CLIENT_TIMEOUT: # remove if connection timed out
					self.clientsLastCommunication.remove(self.clientsLastCommunication[self.clients[i]])
					self.clients.remove(self.clients[i])
				else:
					i += 1
			sleep(0.2)

	def getMyIp(self): # FIN
		checkIpSock = socket(AF_INET, SOCK_DGRAM)
		checkIpSock.connect(('8.8.8.8', 0))  # connecting to a UDP address doesn't send packets
		return checkIpSock.getsockname()[0]

	def getContacts(self, ID):
		# send list of ID's and addresses of nodes that this node[ID] can send to
		raise("Not Implemented exception")

	def shutdown(self): # FIN
		self.isShutdown = True
		upToDateStatus = urllib.urlopen("http://dirser.honor.es/dirSer/status.php").read()
		upToDateStatus = upToDateStatus.replace("\n" + self.getMyIP() + "," + str(self.port), "") # remove this addr
		f = open("upload/status.php", "w")
		f.write(upToDateStatus)
		f.close()
		if !upload(True): # upload and not verbose
			for i in range(2): # try 2 more times
				if upload(True): # break
					break
				if i == 1:
					raise Exception("upload failed")
		sleep(0.5)



def main(): # FIN
	# upload external address and port ..
	server = Server()
	server.start()
	print ">> started"
	cmds = ["shutdown", "exit", "close", "quit"]
	while True:
		inp = raw_input()
		if inp in cmds
			print "shutting down . . ."
			server.shutdown()
		else:
			print "illigal command, avalivablr commands: " + ", ".join(cmds)
		

if __name__ == "__main__":
	main()



