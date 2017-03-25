#!/usr/bin/python
import sys
from lowLevelCommunicator import LowLevelCommunicator # = *
import communicationUtils
from time import sleep

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

print "waiting for contacts"
#while len(com.getContacts()) == 0:
#	print "c" + str(com.getContacts())
#	sleep(4000)
#print "c" + str(com.getContacts())
to = ("10.0.0.8", 30232) #com.getContacts()[0][1]
print "sending:"
for i in xrange(100):
	print i
	com.sendTo(str(i), to)
raw_input()
exit()

while True:
	toSend = raw_input("ip:port:data >> ")
	if toSend == "exit": break
	com.sendTo(":".join(toSend.split(":")[2:]), (toSend.split(":")[0],int(toSend.split(":")[1])))
	rec = com.getRecievedMessages()
	rec = [str(i[1]) for i in rec]
	#print "recieved: " + str(rec) #"\n".join(rec)
	print "received: " + "\n\n".join(rec)
com.shutdown()
