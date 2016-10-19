#!/usr/bin/python

import communicationUtils

class communication:
	def __init__(self, ID, holePunchingIp = "8.8.8.8"):
		port = defaultPort()
		while isPortTaken(self.port):
			port += 1
			if port >= 2^16: port = 2000
		self.communicator = LowlevelCommunicator(port, holePunchingIp, ID)
		self.communicator.startPortProtectionService()
		self.communicator.startRecievingThread(self.port)

	def sendQuery(self, qry):
		toID = self.__getBest
		self.communicator.sendTo(self.__encodeQuerry(qry), toID) # to = (host,port)
		raise("Not implemented execption")

	def recieve(self):#getRecievedQuerriesAndTasks():
		QandT = self.communicator.getRecievedQuerriesAndTasks()
		return self.decode(QandT)

	def decode(self, QuerriesAndTasks):
		if(type(QuerriesAndTasks) == type(list()))
			retLst = []
			for item in QuerriesAndTasks:
				retLst.append(self.__decode(item))
			return retLst
		return self.__decode(QandT) # if single item

	def __decode(QuerryOrThread):
		raise("Not implemented execption")
	def __encodeQuerry(Querry):
		raise("Not implemented execption")
	def __encodeTask(Task):
		raise("Not implemented execption")
		
