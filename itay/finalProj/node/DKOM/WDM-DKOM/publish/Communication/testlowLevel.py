#!/usr/bin/python
import sys
from lowLevelCommunicator import LowLevelCommunicator # = *
import communicationUtils

if len(sys.argv) < 3:
    print "not enought arguments! the input should be:"
    print "script.py <id> <port>"
    exit()

gateway = "192.168.0.1"
print "ip: " + gateway,
print " port: " + sys.argv[2],

com = LowLevelCommunicator(int(sys.argv[2]), (gateway, 12345), sys.argv[1])
com.start()

myIntIps = communicationUtils.GetMachineInternalIps()
print "My internal Ips: " + str([i for i in myIntIps])

while True:
	toSend = raw_input("ip:port:data >> ")
	if toSend == "exit": break
	com.sendTo(":".join(toSend.split(":")[2:]), (toSend.split(":")[0],int(toSend.split(":")[1])))
	rec = com.getRecievedMessages()
	rec = [str(i[1]) for i in rec]
	#print "recieved: " + str(rec) #"\n".join(rec)
	print "received: " + "\n\n".join(rec)
com.shutdown()
