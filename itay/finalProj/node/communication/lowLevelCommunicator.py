#!/usr/bin/python
#import threading
from scapy.all import *
from thread import start_new_thread
from socket import *
from time import sleep, time
import communicationUtils

class LowLevelCommunicator: # FIN
	def __init__(self, port, holePunchingAddr, ID): # FIN
		self.__port = port
		self.__recvFromAddr = {} # store addresses that sended to this node by format {ID:ADDR}
		self.__sendedAndNotResponded = []
		self.__sniffed = []
		self.__rawMessages = {}
		self.__pacTimeout = 1 # 1 = default # in seconds
		self.__isPortProtectionServiceStarted = False
		self.__isRecievingThreadStarted = False
		self.__isSendedValidationThreadStarted = False
		self.__shutdown = False
		self.__holePunchingAddr = holePunchingAddr
		self.__dirSerAddr = communicationUtils.GetDirServerAddr();
		self.__ID = ID
		self.__seq = 0
		self.__recentMessagedIdSeq = [] # last 500 msgs (id,seq)
		self.otherNodes = [] # [(ID,ADDR)...]
		self.allOtherNodes = {} # {ID:ADDR, ...}
		self.EOM = "<EOF>" # end of message
		self.SOM = "<SOM>" # start of message
		self.MAX_SEQ = 2**16
		self.log = open("lowLevelCom.log", "w")
		# self.pcapWriter = PcapWriter("sniffLog" + str(ID) + ".pcap", append=True, sync=True) for debugging

	def start(self): # FIN
		self.startPortProtectionService()
		self.startRecievingThread()
		self.startSendedMsgsValidationThread()
	
	def startPortProtectionService(self): # FIN
		if self.__isPortProtectionServiceStarted: return # already started
		start_new_thread(self.__portProtectionService, (3,)) # 3 = default
		self.__isPortProtectionServiceStarted = True
		self.log.write("port protection started\n")
		self.log.flush()

	def __portProtectionService(self, gapBetweenPunches=3): # FIN
		i = 0
		while not self.__shutdown:
		# optional: maybe block any connection that attemps to bind or use that port
			i += 1
			if i == 6 / 3:
				self.requestContacts()
			else:
				self.log.write("hole punching...\n")
				self.log.flush()
				holePunchPac = IP(dst=self.__holePunchingAddr[0])/UDP(sport=self.__port, dport=self.__holePunchingAddr[1])/str(self.__ID)
				send(holePunchPac, verbose=False)
			sleep(gapBetweenPunches)

	def startSendedMsgsValidationThread(self): #FIN 
		if self.__isSendedValidationThreadStarted: return # already started
		start_new_thread(self.__sendedValidationThread, ())
		self.__isSendedValidationThreadStarted = True
		self.log.write("sended messages validation started\n")
		self.log.flush()
	
	def startRecievingThread(self): # FIN
		if self.__isRecievingThreadStarted: return # already started
		start_new_thread(self.__recievingThread, ())
		self.__isRecievingThreadStarted = True
		self.log.write("recieving started\n")
		self.log.flush()

	def __recievingThread(self): # FIN
		start_new_thread(self.__sniffingThread,())
		while not self.__shutdown:
			for pac in self.__sniffed:
				# check if the packet is valid
				origChecksum = pac[UDP].chksum
				del pac[UDP].chksum
				pac = pac.__class__(str(pac)) # dump to string and rebuild the packet
				if origChecksum != pac[UDP].chksum: # packet is damaged
					continue # ignore this packet
				# then extract data to recData
				try:
					splt = pac[Raw].load.split(",")
					self.__recvFromAddr[splt[0]] = (pac[IP].src, pac[UDP].sport) # add to addresses by ID's dictionary
					if splt[2] == "r": # recieved response => remove from self.__sendedAndNotResponded
						# print "r received" # for debug
						for i in self.__sendedAndNotResponded:
							if i[0] == int(splt[3]): # remove
								# print "removed: " + str(i) # for debug
								self.__sendedAndNotResponded.remove(i)
								break
						# print "sended and not resp: " + str(self.__sendedAndNotResponded) # for debug
						# pac[IP].src == self.__dirSerAddr[0]: # dir server ip
					elif splt[0] == "0": # ID == 0 => its a directory server
						# its the node connections data... use it, save it to list or ID
						for i in eval(",".join(splt[3:])): # list
							if i not in self.otherNodes:
								self.otherNodes.append(i) # (ID, ADDR), ADDR = (IP, PORT)
						self.allOtherNodes.update(dict(self.otherNodes))
					elif splt[2] == "m": # msg
						#if (splt[0], splt[1]) not in self.__rawMessages.keys(): # not recieved yet
						if (splt[0], splt[1]) not in self.__recentMessagedIdSeq: # not recieved yet
							self.__recentMessagedIdSeq.append((int(splt[0]), int(splt[1])))
							if (self.__recentMessagedIdSeq) >= 500:
								self.__recentMessagedIdSeq.pop(0) # remove oldest item
							self.__rawMessages[(int(splt[0]), int(splt[1]))] = ",".join(splt[3:]) # dict[ID, Seq] = data
						self.__sendRecievedResponse(splt)
					else: # unimplemented packet type
						raise Exception("not implemented packet type (LLC reached to else statment)")
				except Exception as e:
					raise Exception("illegal packet, exception: " + str(e))
					#print "recieving Thread err: illegal packet"
					#print "err data: " + str(e)
					#print "packet: \n"
					#pac.show()
			self.__sniffed = []
			sleep(0.1)
	
	def __sniffingThread(self): # FIN
		myIntIps = communicationUtils.GetMachineInternalIps()
		myIntIps = [ip.encode('ascii', 'ignore') for ip in myIntIps] # from unicode to str
		# print "My internal Ips: " + str([i for i in myIntIps])
		pacFilter = lambda p: p.haslayer(UDP) and p[UDP].dport == self.__port and p.haslayer(IP) and p[IP].dst in myIntIps
		stopFilter = lambda x: self.__shutdown
		sniff(lfilter=pacFilter, prn=self.__appendSniffedPac, stop_filter=stopFilter)

	# for debugging:
	#def __demoFilter(self, p):
	#	if p.haslayer(UDP) and p[UDP].dport == self.__port and p.haslayer(IP): #and p[IP].dst in myIntIps
	#		self.pcapWriter.write(p) # for debugging
	#	return p.haslayer(UDP) and p[UDP].dport == self.__port and p.haslayer(IP) #and p[IP].dst in myIntIps
	
	def __appendSniffedPac(self, p): # FIN
		#print "appended: ",
		#p.summary()
		self.__sniffed.append(p)
	
	def sendTo(self, msg, to): # FIN
		if type(to) == type(list()):
			for node in to:
				self.__sendTo(msg, Node)
		else: # to single node
			self.__sendTo(msg, to)

	# returning recieved messages in format: [(ID1, msg1), (ID2, msg2), (ID3, msg3)...]
	def getReceivedMessages(self): # FIN
		if len(self.__rawMessages) == 0: # if raw messages empty exit
			return []
		messages = []
		sortedRawMessagesKeys = list(sorted(self.__rawMessages.keys())) # sort by (primaryElement, secondaryElement)
		isMsgValid = True
		lastSeqId = sortedRawMessagesKeys[0] # first key[0] = first key id
		lastKeys = [sortedRawMessagesKeys[0]] # initialize with the first key
		msgParts = [] #[self.__rawMessages[sortedRawMessagesKeys[0]]]
		for i in sortedRawMessagesKeys: #[1:]:
			#print "i: ", type(i), " last: ", type(lastSeqId)
			if self.__rawMessages[i] == self.SOM:
				isMsgValid = True # reinitialize for the msg
				lastKeys = [] # reinitialize for the msg
				msgParts = [] # reinitialize for the msg
			elif isMsgValid and lastSeqId[0] == i[0] and (lastSeqId[1] + 1) % self.MAX_SEQ == i[1] and self.__rawMessages[i] == self.EOM:
				lastKeys.append(i)
				if isMsgValid:
					messages.append((i[0], "".join(msgParts))) # ID, msg
					for key in lastKeys: # remove "used" raw messages
						self.__rawMessages.pop(key)
					isMsgValid = False
				#else:
				#	isMsgValid = True # reinitialize for the next msg
				#lastKeys = [] # reinitialize for the next msg
				#msgParts = [] # reinitialize for the next msg
			elif isMsgValid and lastSeqId[0] == i[0] and (lastSeqId[1] + 1) % self.MAX_SEQ == i[1]: # same id and next seq
				msgParts.append(self.__rawMessages[i])
				lastKeys.append(i)
			#elif lastSeqId[0] != i[0]: # start of a msg from another node, ID changed
			#	isMsgValid = True # reinitialize for the msg
			#	lastKeys = [i] # reinitialize for the next msg
			#	msgParts = [self.__rawMessages[i]] # reinitialize for the next msg
			else: # lastSeqId[0] == i[0] and lastSeqId[1] + 1 != i[1]
				isMsgValid = False
			lastSeqId = i
		return messages # in the format (ID, msg)

	def __sendedValidationThread(self): # FIN
		"""
		re-send packets that havn't recieved or recieved incorrectly
		"""
		while not self.__shutdown:
			for i in self.__sendedAndNotResponded: # i = (seq, time(), pac)
				if time() - i[1] >= self.__pacTimeout:
					self.log.write("re sended: " + str(i[2]) + "\n")
					self.log.flush()
					send(i[2], verbose = False)
					i[1] = time()
					# print "re-sent: " + str(i) # for debug
			sleep(0.2)

	def __sendTo(self, msg, to): # FIN
		# to = (ip, port)
		#to = self.getAddrById(toID)
		self.log.write("sending: " + msg + "\n")
		self.log.flush()
		msgIndicatorLen = len("m,") # indicates thats a message
		maxIdAndSeqLen = len(str(2**48)) + len(str(self.MAX_SEQ))
		maxPortLength = len(str(2**16))
		dataPerPac = (508 - maxIdAndSeqLen - maxPortLength - msgIndicatorLen) # 508 = for sure safe length
		numToSend = int(len(msg) / dataPerPac) + 1 # round down + 1 =~ round up
		toSend = []
		toSend.append(IP(dst=to[0])/UDP(sport=self.__port, dport=to[1])/(str(self.__ID) + "," + str(self.__seq) + ",m," + self.SOM)) # start message
		self.__sendedAndNotResponded.append([self.__seq, time(), toSend[-1]])
		self.__incSeq()
		for i in xrange(numToSend - 1): # split data to packets with max len of "dataPerPac"
			# ID,Seq,messageIndicator,data
			# the response address would be found by the ID
			raw = str(self.__ID) + "," + str(self.__seq) + ",m," + msg[i*dataPerPac:(i+1)*dataPerPac]
			toSend.append(IP(dst=to[0])/UDP(sport=self.__port, dport=to[1])/raw)
			self.__sendedAndNotResponded.append([self.__seq, time(), toSend[-1]])
			self.__incSeq()
		toSend.append(IP(dst=to[0])/UDP(sport=self.__port, dport=to[1])/
			(str(self.__ID) + "," + str(self.__seq) + ",m," + msg[(numToSend-1)*dataPerPac:])) # last data packet
		self.__sendedAndNotResponded.append([self.__seq, time(), toSend[-1]])
		self.__incSeq()
		toSend.append(IP(dst=to[0])/UDP(sport=self.__port, dport=to[1])/(str(self.__ID) + "," + str(self.__seq) + ",m," + self.EOM)) # end message
		self.__sendedAndNotResponded.append([self.__seq, time(), toSend[-1]])
		self.__incSeq()
		#print "tosend: " + str(toSend) # fir debugging
		send(toSend, verbose = False)

	def __sendRecievedResponse(self, pacDataSplt): # FIN
		self.log.write("sended recieved response to: " + str(pacDataSplt) + "\n")
		self.log.flush()
		splt = pacDataSplt # pacData.split(",")
		try:
			to = self.__recvFromAddr[splt[0]] # self.getAddrById(int(splt[0]))
		except Exception as e:
			print "send recv response err: " + str(e)
		# ID,Seq,recvResponseIndicator,recPacSeq
		raw = str(self.__ID) + "," + str(self.__seq) + ",r," + splt[1] #r=recieved , splt[1] = other node's seq
		# print "sending resp: " + raw # for debugging
		send(IP(dst=to[0])/UDP(sport=self.__port, dport=to[1])/raw, verbose = False)

	def __incSeq(self): # FIN
		""" icrease sequence indicator """
		self.__seq += 1
		if self.__seq >= self.MAX_SEQ: self.__seq = 0 # reset seq # like % but faster
	
	def shutdown(self): # FIN
		self.__shutdown = True
		sleep(1)

	def refreshContacts(self):
		self.log.write("refreshed contacts\n")
		self.log.flush()
		self.otherNodes = []
		self.requestContacts()

	def requestContacts(self):
		self.log.write("requested for contacts\n")
		self.log.flush()
		requestPac = IP(dst=self.__dirSerAddr[0])/UDP(sport=self.__port, dport=self.__dirSerAddr[1])/(">" + str(self.__ID))
		send(requestPac, verbose=False)

	def getContacts(self):
		return self.otherNodes[0:] # copy

	def getAllPossibleContacts(self): # return {ID:ADDR,...} for all nodes from all times
		ret = self.__recvFromAddr.copy()
		ret.update(self.allOtherNodes)
		return ret
