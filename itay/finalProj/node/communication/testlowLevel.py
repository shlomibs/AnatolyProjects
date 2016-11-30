#!/usr/bin/python
import sys
from lowLevelCommunicator import LowLevelCommunicator # = *

com = LowLevelCommunicator(int(sys.argv[2]), ("10.0.0.138", 12345), sys.argv[1])
com.startPortProtectionService()
com.startRecievingThread()


while True:
	toSend = raw_input("ip:port:data >> ")
	if toSend == "exit": break
	com.sendTo(":".join(toSend.split(":")[2:]), (toSend.split(":")[0],int(toSend.split(":")[1])))
	rec = com.getRecievedMessages()
	rec = [str(i) for i in rec]
	print "recieved: " + "\n".join(rec)
