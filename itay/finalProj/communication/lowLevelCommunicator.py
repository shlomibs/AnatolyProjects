#!/usr/bin/python
import time
import threading


class LowLevelCommunicator:
	def startPortProtectionService(self, port):
		# if self.ports is not defined create it
		self.ports.append(port)

		raise Exception("Not implemented exception")
	def startRecievingThread(port):
		raise Exception("Not implemented exception")
	def recievingThread():
		raise Exception("Not implemented exception") # sniff and filter packets
	def sendTo(self, msg, to):
		if type(to) == type(list()):
			for node in to:
				self.__sendTo(msg, Node)
		else:
			self.__sendTo(msg, to)
	def __sendTo(msg, to):
		raise Exception("Not implemented exception")
