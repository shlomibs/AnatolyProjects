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
	def __init__(self, port, holePunchingAddr, ID):
		self.port = port
		self.recived = [] # item in recieved is (IDfrom, id
		self.recvFromAddr = {} # store addresses that sended to this node by format {ID:ADDR}
		self.sendedAndNotResponded = []
		self.sniffed = []
		self.rawMessages = {}
		self.pacTimeout = 5 # 5 = default
		self.isPortProtectionServiceStarted = False
		self.isRecievingThreadStarted = False
		self.__shutdown = False
		self.holePunchingAddr = holePunchingAddr
		self.ID = ID
		self.seq = 0
		self.EOM = "<EOF>" # end of message
		self.MAX_SEQ = 2^16

	def startPortProtectionService(self): # FIN
		if self.isPortProtectionServiceStarted: return # already started
		start_new_thread(self.__portProtectionService, (3,)) # 3 = default
		self.isPortProtectionServiceStarted = True

	def __portProtectionService(self, gapBetweenPunches): # FIN (for now)
		"""
		hole punching only for now
		"""
		while not self.__shutdown:
		#next: maybe block any connection that attemps to bind or use that port
			holePunchPac = IP(dst=self.holePunchingAddr[0])/UDP(sport=self.port, dport=self.holePunchingAddr[1])/str(self.ID)
			send(holePunchPac, verbose=False)
			sleep(gapBetweenPunches)
		#raise Exception("Not implemented exception")

	def startRecievingThread(self): # FIN
		if self.isRecievingThreadStarted: return # already started
		start_new_thread(self.__recievingThread, ())
		self.isRecievingThreadStarted = True

	def __recievingThread(self): # FIN
		start_new_thread(self.__sniffingThread,())
		while not self.__shutdown:
			if len(self.sniffed) > 0:
				print "sniffed: ",
				print self.sniffed
			# TODO: check the packets are valid
			# then extract data to recData
			for pac in self.sniffed:
				try:
					splt = pac[Raw].split(",")
					recvFromAddr[splt[0]] = (pac[IP].src, pac[UDP].sport) # add to addresses by ID's dictionary
					if splt[2] == "r": # recieved response => remove from self.sendedAndNotResponded
						for i in self.sendedAndNotResponded:
							if i[0] == str(self.seq): # remove
								self.sendedAndNotResponded.remove(i)
								break
					#elif pac[IP].src == communicationUtils.getDirServerAddr()[0]: # dir server ip
						# its the node connections data... use it, save it to list or ID
					elif splt[2] == "m": # msg
						if (splt[0], splt[1]) not in self.RawMessages.keys(): # not recieved yet
							self.rawMessages[(int(splt[0]), int(splt[1]))] = ",".join(splt[3:]) # dict[ID, Seq] = data
						self.__sendRecievedResponse(splt[3])
					else: # unimplemented packet type
						raise Exception("not implemented packet type (LLC reached to else statment)")
				except Exception as e:
					print "recieving Thread err: illegal packet"
					print "err data: " + str(e)
					print "packet: \n"
					pac.show()
			self.sniffed = []
			sleep(0.1)
		#raise Exception("Not implemented exception") # sniff and filter packets
	
	def __sniffingThread(self): # FIN
		myIntIps = communicationUtils.GetMachineInternalIps()
		print "My internal Ips: " + str([i for i in myIntIps])
		pacFilter = lambda p: p.haslayer(UDP) and p[UDP].dport == self.port and p.haslayer(IP) and p[IP].dst in myIntIps
		stopFilter = lambda x: self.__shutdown
		sniff(lfilter = pacFilter, prn = self.sniffed.append, stop_filter = stopFilter)
		print "sniffed unexpectly exited"

	def sendTo(self, msg, to): # FIN
		if type(to) == type(list()):
			for node in to:
				self.__sendTo(msg, Node)
		else: # to single node
			self.__sendTo(msg, to)

	def getRecievedMessages(self): # FIN
		print "sniffed: ",
		print self.sniffed
		if len(self.rawMessages) == 0: # if raw messages empty exit
			return []
		messages = []
		sortedRawMessagesKeys = list(sorted(self.rawMessages.keys())) # sort by (primaryElement, secondaryElement)
		isMsgValid = True
		lastSeqId = sortedRawMessagesKeys[0][0] # first key[0] = first key id
		lastKeys = [sortedRawMessagesKeys[0]] # initialize with the first key
		msgParts = [self.rawMessages[sortedRawMessagesKeys[0]]]
		for i in sortedRawMessagesKeys[1:]:
			if lastSeqId[0] == i[0] and (lastSeqId[1] + 1) % self.MAX_SEQ == i[1] and self.rawMessages[i] == self.EOM:
				lastKeys.append(i)
				if isMsgValid:
					messages.append((i[0], "".join(msgParts))) # ID, msg
					for key in lastKeys: # remove "used" raw messages
						self.rawMessages.pop(key)
				else:
					isMsgValid = True # reinitialize for the next msg
				lastKeys = [] # reinitialize for the next msg
				msgParts = [] # reinitialize for the next msg
			elif lastSeqId[0] == i[0] and lastSeqId[1] + 1 == i[1]: # same id and next seq
				msgParts.append(self.rawMessages[i])
				lastKeys.append(i)
			elif lastSeqId[0] != i[0]: # start of msg from another node
				isMsgValid = True # reinitialize for the msg
				lastSeqId[0] = i[0]
				lastKeys = [] # reinitialize for the next msg
				# msgParts = [] # reinitialize for next the msg
				# msgParts.append(self.rawMessages[i])
				msgParts = [self.rawMessages[i]] # reinitialize for the next msg
			else: # lastSeqId[0] == i[0] and lastSeqId[1] + 1 != i[1]
				isMsgValid = False
		return messages # in the format (ID, msg)

	def __sendedValidationThread(): # FIN
		"""
		re-send packets that havn't recieved or recieved incorrectly
		"""
		while not self.__shutdown:
			for i in self.sendedAndNotResponded: # i = (seq, time(), pac)
				if time() - i[1] >= self.pacTimeout:
					send(i[2])
					i[1] = time()
			sleep(0.2)# reinitialize for the msg

	def __sendTo(self, msg, to): # FIN
		# to = (ip, port)
		#to = self.getAddrById(toID)
		msgIndicatorLen = len("m,") # indicates thats a message
		maxIdAndSeqLen = len(str(2^32)) + len(str(self.MAX_SEQ))
		maxPortLength = len(str(2^16))
		dataPerPac = (508 - maxIdAndSeqLen - maxPortLength - msgIndicatorLen) # 508 = for sure safe length
		numToSend = int(len(msg) / dataPerPac) + 1 # roud down + 1 =~ round up
		toSend = []
		for i in xrange(numToSend - 1): # split data to packets with max len of "dataPerPac"
			# ID,Seq,messageIndicator,data
			# the response address would be found by the ID
			raw = str(self.ID) + "," + str(self.seq) + ",m," + msg[i*dataPerPac:(i+1)*dataPerPac]
			toSend.append(IP(dst=to[0])/UDP(sport=self.port, dport=to[1])/raw)
			self.sendedAndNotResponded.append((self.seq, time(), toSend[-1]))
			self.__incSeq()
		toSend.append(IP(dst=to[0])/UDP(sport=self.port, dport=to[1])/
			(str(self.ID) + "," + str(self.seq) + ",m," + msg[(numToSend-1)*dataPerPac:])) # last data packet
		self.sendedAndNotResponded.append((self.seq, time(), toSend[-1]))
		self.__incSeq()
		toSend.append(IP(dst=to[0])/UDP(sport=self.port, dport=to[1])/(str(self.ID) + "," + str(self.seq) + ",m," + self.EOM)) # end message
		self.sendedAndNotResponded.append((self.seq, time(), toSend[-1]))
		self.__incSeq()
		print "tosend: " + str(toSend)
		sendp(toSend) #, verbose = False)
		#self.sendedAndNotResponded.append(self.seq, time(), toSend[-1])

	def __sendRecievedResponse(self, pacData): # FIN
		splt = pacData.split(",")
		try:
			to = recvFromAddr[splt[0]] # self.getAddrById(int(splt[0]))
		except Exception as e:
			print "send recv response err: " + str(e)
		# ID,Seq,recvResponseIndicator,recPacSeq
		raw = str(self.ID) + "," + str(self.seq) + ",r," + splt[1] #r=recieved 
		send(IP(dst=to[0])/UDP(sport=self.port, dport=to[1])/raw)

	def __incSeq(self): # FIN
		""" icrease sequence indicator """
		self.seq += 1
		if self.seq >= self.MAX_SEQ: self.seq = 0 # reset seq # like % but faster
	
	def shutdown():
		self.__shutdown = True






