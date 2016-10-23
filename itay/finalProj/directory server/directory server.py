from uploadToDirSer import upload
from socket import *
from thread import start_new_thread
from time import time

class Server:
	def __init__(self):
		self.s = socket(AF_INET, SOCK_DGRAM)
		self.s.bind(("0.0.0.0", port))
		self.isShutdown = False
		self.clients = [] # (ID, address)
		self.clientsLastCommunication = {} # class
		self.MAX_NODES_NUM = 20 # to fit to one packet
		self.CLIENT_TIMEOUT = 3 * 4

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
			if data[-1] == ">"
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

	def getContacts(self, ID):
		raise("Not Implemented exception")

	def shutdown(self): # FIN
		self.isShutdown = True
		sleep(0.5)



def main():
	# upload external address and port ..
	server = Server()
	server.start()
	while True:
		inp = raw_input()
		if inp in ["shutdown", "exit", "close", "quit"]:
			print "shutting down . . ."
			server.shutdown()

if __name__ == "__main__":
	main()



