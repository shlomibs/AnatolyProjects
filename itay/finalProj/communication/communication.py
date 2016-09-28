#!/usr/bin/python

from communicationUtils import *
from scapy.all import *

class communication:
	def	__init__(self):
		self.communicator = LowlevelCommunicator
		self.port = defaultPort()
		while isPortTaken(self.port):
			self.port += 1
		self.communicator.startPortProtectionService(self.port)
		self.communicator.startRecievingThread(self.port)
	def sendQuery(self, qry):
		raise("Not implemented execption")
	def recieve(self):#getRecievedQuerriesAndTasks():
		QandT = self.communicator.getRecievedQuerriesAndTasks()
		return self.decode(QandT)
	def decode(self, QandT):
		if(type(QandT) == type(list()))
			retLst = []
			for item in QandT:
				retLst.append(self.__decode(item))
			return retLst
		return self.__decode(QandT) # if single item
	def __decode():
		raise("Not implemented execption")
		
