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

	def sendQuery(self, qry): # FIN
		toID = self.getBestContactId(qry)
		self.communicator.sendTo(self.communicator.encoder.encodeQuerry(qry), toID) # to = (host,port)

	def sendQuery(self, task): # FIN
		toID = self.getBestContactId(task)
		self.communicator.sendTo(self.communicator.encoder.encodeTask(task), toID) # to = (host,port)

	def recieve(self):#getRecievedQuerriesAndTasks(): # FIN
		QandT = self.communicator.getRecievedQuerriesAndTasks()
		return self.communicator.encoder.decode(QandT)

	def getBestContactId(self, qry):
		raise("Not implemented execption")
