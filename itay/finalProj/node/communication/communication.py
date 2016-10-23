#!/usr/bin/python
import communicationUtils

class communication:
	def __init__(self, ID, communicationKey, holePunchingAddr = communicationUtils.getDirServerAddr()):
		port = defaultPort()
		while isPortTaken(self.port):
			port += 1
			if port >= 2^16: port = 2000
		self.communicator = LowlevelCommunicator(port, holePunchingAddr, ID, communicationKey)
		self.communicator.startPortProtectionService()
		self.communicator.startRecievingThread(self.port)

	def sendQuery(self, qry):
		toID = self.__getBest...
		self.communicator.sendTo(self.communicator.encoder.encodeQuerry(qry), toID) # to = (host,port)
		raise("Not implemented execption")

	def recieve(self):#getRecievedQuerriesAndTasks(): # FIN
		QandT = self.communicator.getRecievedQuerriesAndTasks()
		return self.communicator.encoder.decode(QandT)
