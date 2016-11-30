#!/usr/bin/python
import sys
from py_compile import compile
compile("communicationUtils.py")
compile("lowLevelCommunicator.py")
from lowLevelCommunicator import LowLevelCommunicator # = *
import communicationUtils

com = LowLevelCommunicator(int(sys.argv[2]), ("192.168.11.254", 12345), sys.argv[1])
com.startPortProtectionService()
com.startRecievingThread()


myIntIps = communicationUtils.GetMachineInternalIps()
print "My internal Ips: " + str([i for i in myIntIps])

while True:
	toSend = raw_input("ip:port:data >> ")
	if toSend == "exit": break
	com.sendTo(":".join(toSend.split(":")[2:]), (toSend.split(":")[0],int(toSend.split(":")[1])))
	rec = com.getRecievedMessages()
	rec = [str(i) for i in rec]
	print "recieved: " + "\n".join(rec)
