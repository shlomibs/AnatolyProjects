#!/usr/bin/python
#import threading
from thread import start_new_thread
from socket import *
from scapy.all import *
from time import sleep, time
from encoder import Encoder

class LowLevelCommunicator:
	"""
	optional: using scapy for communicating hiddenly
	for now: communicate via socket
	"""
	def __init__(self, port, holePunchingIp, ID):
		self.port = port
		self.recived = [] # item in recieved is (IDfrom, 
		self.sendedAndNotResponded = []
		self.sniffed = []
		self.pacTimeout = 5 # 5 = default
		self.isPortProtectionServiceStarted = False
		self.isRecievingThreadStarted = False
		self.shutdown = False
		self.holePunchingIp = holePunchingIp
		self.ID = ID
		self.seq = 0
		self.EOM = "<EOF>" # end of message

	def startPortsProtectionService(self): # FIN
		if self.isPortProtectionServiceStarted: return # already started
		start_new_thread(portProtectionService, (3,)) # 3 = default
		self.isPortProtectionServiceStarted = True

	def __portProtectionService(self, gapBetweenPunches): # FIN (for now)
		"""
		hole punching only for now
		next: maybe block any connection that attemps to bind or use that port
		"""
		while !self.shutdown:
			holePunchPac = IP(dst=self.holePunchingIp)/UDP(dport=port)
			sendp(holePunchPacs)
			sleep(gapBetweenPunches)
		#raise Exception("Not implemented exception")

	def startRecievingThread(self): # FIN
		if self.isRecievingThreadStarted: return # already started
		start_new_thread(self.__recievingThread, ())
		self.isRecievingThreadStarted = True

	def __recievingThread(self): #():
		start_new_thread(self.__sniffingThread,())
		while !self.shutdown:
			# TODO: check the packets are valid
			# then extract data to recData
			self.recieved.append(recData)
			sleep(0.1)
		raise Exception("Not implemented exception") # sniff and filter packets
	
	def __sniffingThread(self): #(): # FIN
		sniff(prn=self.sniffed.append)
		
	def sendTo(self, msg, toIP): # FIN
		if type(to) == type(list()):
			for node in to:
				self.__sendTo(msg, Node)
		else: # to single node
			self.__sendTo(msg, to)

	def __sendedValidationThread():
		while !self.shutdown:
			for i in self.sendedAndNotResponded: # i = (seq, time(), pac)
				if time() - i[1] >= self.pacTimeout:
					sendp(i[2])
					i[1] = time()
				sleep(0.2)

	def __sendTo(self, msg, toID): # FIN
		# to = ID #(ip, port)
		to = self.getAddrById(toID)
		maxIdAndSeqLen = len(str(2^32)) + len(str(2^16))
		maxPortLength = len(str(2^16))
		dataPerPac = (508 - maxIdAndSeqLen - maxPortLength) # 508 = for sure safe length
		numToSend = int(len(msg) / dataPerPac) + 1 # roud down + 1 =~ round up
		toSend = []
		for i in xrange(numToSend - 1): # split data to packets with max len of "dataPerPac"
			# ID,Seq,data
			# the response address would be found by the ID
			raw = str(self.ID) + "," + str(self.seq) + "," + msg[i*dataPerPac:(i+1)*dataPerPac]
			toSend.append(IP(dst=to[0])/UDP(dport=to[1])/raw)
			self.sendedAndNotResponded.append(self.seq, time(), toSend[-1])
			self.__incSeq()
		toSend.append(IP(dst=to[0])/UDP(dport=to[1])/(str(self.ID) + "," + str(self.seq) + "," + msg[(numToSend-1)*dataPerPac:])) # last data packet
		self.sendedAndNotResponded.append(self.seq, time(), toSend[-1])
		self.__incSeq()
		toSend.append(IP(dst=to[0])/UDP(dport=to[1])/str(self.ID) + "," + str(self.seq) + "," + self.EOM) # end message
		self.sendedAndNotResponded.append(self.seq, time(), toSend[-1])
		self.__incSeq()
		sendp(tosend)
		self.sendedAndNotResponded.append(self.seq, time(), toSend[-1])

	def getAddrById(ID):
		raise Exception("Not implemented exception")

	def __incSeq(self): # FIN
		""" icrease sequence indicator """
		self.seq += 1
		if self.seq >= 2^16: self.seq = 0 # reset seq





