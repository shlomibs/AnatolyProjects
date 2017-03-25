#!/usr/bin/python
from time import sleep
import communicationUtils
from encoder import Encoder
from lowLevelCommunicator import LowLevelCommunicator

class Communication:
	def __init__(self, ID, communicationKey, holePunchingAddr = communicationUtils.GetDirServerAddr()):
		self.port = communicationUtils.defaultPort()
		while communicationUtils.IsPortTaken(self.port): # take over a port
			self.port += 1
			if self.port >= 2**16:
				self.port = 2000 # after saved ports
		self.__encoder = Encoder(communicationKey)
		with open("config.cfg", "w") as f:
			f.write(self.__encoder.encrypt(str(self.port))) # save the port for controller
		self.__communicator = LowLevelCommunicator(self.port, holePunchingAddr, ID)
		self.__communicator.start()

	def send(self, qryOrTsk, toId): # FIN
		#toId = self.getBestContactId(qryOrTsk)
		self.__communicator.log.write("communication, sending: " + qryOrTsk + "\n")
		self.__communicator.log.flush()
		self.__communicator.sendTo(self.__encoder.encrypt(qryOrTsk), self.getAddrById(toId)) # to = (host,port)
		#self.__communicator.sendTo(qryOrTsk, self.getAddrById(toId)) # to = (host,port)

	def getReceivedMessages(self): # getRecievedQuerriesAndTasks(): # FIN
		QandT = self.__communicator.getReceivedMessages() #getRecievedQuerriesAndTasks()
		self.__communicator.log.write("communication, recieved messages: " + str(QandT) + "\n")
		self.__communicator.log.flush()
		return self.__encoder.decrypt(QandT)

	def getAddrById(self, ID):
		contacts = dict(self.__communicator.getContacts())
		try:
			return contacts[str(ID)]
		except:
			try:
				return self.__communicator.getAllPossibleContacts()[str(ID)]
			except Exception as e:
				raise e

	def refreshContacts(self, timeout = 0.2):
		self.__communicator.refreshContacts()
		sleep(timeout)

	def getContacts(self):
		return [c[0] for c in self.__communicator.getContacts()] # only id's