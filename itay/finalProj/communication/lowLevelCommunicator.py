#!/usr/bin/python
#import threading
from thread import start_new_thread
from socket import *
from scapy.all import *
from time import sleep

class LowLevelCommunicator:
	"""
	optional: using scapy for communicating hiddenly
	for now: communicate via socket
	"""
	def __init__(self, port, holePunchingIp, ID):
		self.port = port
		self.recived = {}
		self.isPortProtectionServiceStarted = False
		self.isRecievingThreadStarted = False
		self.shutdown = False
		self.holePunchingIp = holePunchingIp
		self.ID = ID
		self.seq = 0
		self.EOM = "<EOF>" # end of message

	def startPortsProtectionService(self): #FIN
		if self.isPortProtectionServiceStarted: return # already started
		start_new_thread(portProtectionService, (3,)) # 3 = default
		self.isPortProtectionServiceStarted = True

	def __portProtectionService(self, gapBetweenPunches): #FIN
		"""
		hole punching only for now
		next: maybe block any connection that attemps to bind or use that port
		"""
		while !self.shutdown:
			holePunchPac = IP(dst=self.holePunchingIp)/UDP(dport=port)
			sendp(holePunchPacs)
			sleep(gapBetweenPunches)
		#raise Exception("Not implemented exception")

	def startRecievingThread(self): #FIN
		if self.isRecievingThreadStarted: return # already started
		start_new_thread(self.__recievingThread, (,))
		self.isRecievingThreadStarted = True

	def __recievingThread(self):
		# check the packets are valid
		# then extract data to recData
		self.recieved.append(recData)
		raise Exception("Not implemented exception") # sniff and filter packets

	def sendTo(self, msg, toIP): #FIN
		if type(to) == type(list()):
			for node in to:
				self.__sendTo(msg, Node)
		else: # to single node
			self.__sendTo(msg, to)

	def __sendTo(self, msg, toID): #FIN
		# to = ID #(ip, port)
		
		maxIdAndSeqLen = len(str(2^32)) + len(str(2^16))
		maxPortLength = len(str(2^16))
		dataPerPac = (508 - maxIdAndSeqLen - maxPortLength) # 508 = for sure safe length
		numToSend = int(len(msg) / dataPerPac) + 1 # roud down + 1 =~ round up
		toSend = []
		for i in xrange(numToSend - 1):
			# ID,Seq,data
			# the response address would be found by the ID
			raw = str(self.ID) + "," + str(self.seq) + "," + msg[i*dataPerPac:(i+1)*dataPerPac]
			self.__incSeq()
			toSend.append(IP(dst=to[0])/UDP(dport=to[1])/raw)
		toSend.append(IP(dst=to[0])/UDP(dport=to[1])/(str(self.ID) + "," + str(self.seq) + "," + msg[(numToSend-1)*dataPerPac:]))
		self.__incSeq()
		toSend.append(IP(dst=to[0])/UDP(dport=to[1])/str(self.ID) + "," + str(self.seq) + "," + self.EOM) # end message
		self.__incSeq()
		sendp(tosend)
		
	def __incSeq(self): #FIN
		""" icrease sequence indicator """
		self.seq += 1
		if self.seq >= 2^16: self.seq = 0









