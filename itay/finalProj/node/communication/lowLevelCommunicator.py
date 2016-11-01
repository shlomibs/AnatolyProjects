#!/usr/bin/python
#import threading
from thread import start_new_thread
from socket import *
from scapy.all import *
from time import sleep, time
import communicationUtils

class LowLevelCommunicator:
	"""
	optional: using scapy for communicating hiddenly
	for now: communicate via socket
	"""
	def __init__(self, port, holePunchingAddr, ID,):
		self.port = port
		self.recived = [] # item in recieved is (IDfrom, id
		self.sendedAndNotResponded = []
		self.sniffed = []
		self.pacTimeout = 5 # 5 = default
		self.isPortProtectionServiceStarted = False
		self.isRecievingThreadStarted = False
		self.shutdown = False
		self.holePunchingAddr = holePunchingAddr
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
		"""
		while !self.shutdown:
		next: maybe block any connection that attemps to bind or use that port
			holePunchPac = IP(dst=self.holePunchingAddr[0])/UDP(sport=self.port, dport=holePunchingAddr[1])/str(self.ID)
			send(holePunchPacs)
			sleep(gapBetweenPunches)
		#raise Exception("Not implemented exception")

	def startRecievingThread(self): # FIN
		if self.isRecievingThreadStarted: return # already started
		start_new_thread(self.__recievingThread, ())
		self.isRecievingThreadStarted = True

	def __recievingThread(self): #():
		start_new_thread(self.__sniffingThread,())
		while not self.shutdown:
			# TODO: check the packets are valid
			# then extract data to recData
			for pac in self.sniffed:
				try:
					splt = pac[Raw].split(",")
					if splt[2] == "r": # recieved response => remove from self.sendedAndNotResponded
						for i in self.sendedAndNotResponded:
							if i[0] == str(self.seq): # remove
								self.sendedAndNotResponded.remove(i)
								break
					if pac[IP].src == communicationUtils.getDirServerAddr()[0]: # dir server ip
						# its the node connections data... use it, save it to list or ID
				except Exception as e:
					print "recieving Thread err: illegal packet"
					print "packet: \n" + str(e)
			
			#if recData is recievedRespone: elf.sendedAndNotResponded.remove(response)
			#else: self.recieved.append(recData)
			sleep(0.1)
		raise Exception("Not implemented exception") # sniff and filter packets
	
	def __sniffingThread(self): #(): # FIN
		sniff(lfilter = lambda p:p.haslayer(UDP) and p[UDP].dport == self.port, prn = self.sniffed.append)
		
	def sendTo(self, msg, to): # FIN
		if type(to) == type(list()):
			for node in to:
				self.__sendTo(msg, Node)
		else: # to single node
			self.__sendTo(msg, to)

	def __sendedValidationThread(): # FIN
		"""
		re-send packets that havn't recieved or recieved incorrectly
		"""
		while not self.shutdown:
			for i in self.sendedAndNotResponded: # i = (seq, time(), pac)
				if time() - i[1] >= self.pacTimeout:
					send(i[2])
					i[1] = time()
			sleep(0.2)

	def __sendTo(self, msg, to): # FIN
		# to = (ip, port)
		#to = self.getAddrById(toID)
		msgIndicatorLen = len("m,") # indicates thats a message
		maxIdAndSeqLen = len(str(2^32)) + len(str(2^16))
		maxPortLength = len(str(2^16))
		dataPerPac = (508 - maxIdAndSeqLen - maxPortLength - msgIndicatorLen) # 508 = for sure safe length
		numToSend = int(len(msg) / dataPerPac) + 1 # roud down + 1 =~ round up
		toSend = []
		for i in xrange(numToSend - 1): # split data to packets with max len of "dataPerPac"
			# ID,Seq,messageIndicator,data
			# the response address would be found by the ID
			raw = str(self.ID) + "," + str(self.seq) + ",m," + msg[i*dataPerPac:(i+1)*dataPerPac]
			toSend.append(IP(dst=to[0])/UDP(sport=self.port, dport=to[1])/raw)
			self.sendedAndNotResponded.append(self.seq, time(), toSend[-1])
			self.__incSeq()
		toSend.append(IP(dst=to[0])/UDP(sport=self.port, dport=to[1])/
			(str(self.ID) + "," + str(self.seq) + ",m," + msg[(numToSend-1)*dataPerPac:])) # last data packet
		self.sendedAndNotResponded.append(self.seq, time(), toSend[-1])
		self.__incSeq()
		toSend.append(IP(dst=to[0])/UDP(sport=self.port, dport=to[1])/(str(self.ID) + "," + str(self.seq) + ",m," + self.EOM) # end message
		self.sendedAndNotResponded.append(self.seq, time(), toSend[-1])
		self.__incSeq()
		send(tosend)
		#self.sendedAndNotResponded.append(self.seq, time(), toSend[-1])

	def __sendRecievedResponse(self, pac): # FIN
		splt = pac.split(",")
		to = self.getAddrById(int(splt[0]))
		# ID,Seq,recvResponseIndicator,recPacSeq
		raw = str(self.ID) + "," + str(self.seq) + ",r," + splt[1] #r=recieved 
		send(IP(dst=to[0])/UDP(sport=self.port, dport=to[1])/raw)

	def __incSeq(self): # FIN
		""" icrease sequence indicator """
		self.seq += 1
		if self.seq >= 2^16: self.seq = 0 # reset seq





