#!/usr/bin/python
import communicationUtils
from encoder import Encoder
from lowLevelCommunicator import LowLevelCommunicator

class Communication:
	def __init__(self, ID, communicationKey, holePunchingAddr = communicationUtils.getDirServerAddr()):
		self.port = defaultPort()
		while communicationUtils.isPortTaken(self.port): # take over a port
			self.port += 1
			if self.port >= 2^16:
				self.port = 2000 # after saved ports
		self.encoder = Encoder(communicationKey)
		self.communicator = LowlevelCommunicator(port, holePunchingAddr, ID)
		self.communicator.start()
		self.connectedNodes = []

	def sendQuery(self, qry): # FIN
		toID = self.getBestContactId(qry)
		self.communicator.sendTo(self.encoder.encodeQuerry(qry), toID) # to = (host,port)

	def sendQuery(self, task): # FIN
		toID = self.getBestContactId(task)
		self.communicator.sendTo(self.encoder.encodeTask(task), toID) # to = (host,port)

	def recieve(self):#getRecievedQuerriesAndTasks(): # FIN
		QandT = self.communicator.getRecievedQuerriesAndTasks()
		return self.encoder.decode(QandT)

	def getBestContactId(self, qry):
		raise("Not implemented execption")

	def getAddrById(ID):
		dirSerAddr = communicationUtils.getDirServerAddr()
		raise Exception("Not implemented exception")
