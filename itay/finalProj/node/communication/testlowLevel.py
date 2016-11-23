#!/usr/bin/python
import lowLevelCommunicator

com = LowLevelCommunicator(9999, "192.168.1.176", input("ID"))
com.startPortProtectionService()
com.startRecievingThread(self.port)


while True:
	toSend = raw_input("ip:port:data")
	com.sendTo(":".join(toSend.split(":")[2:]), (toSend.split(":")[0],int(toSend.split(":")[1])))
	rec = getRecievedMessages()
	rec = [str(i) for i in rec]
	print "recieved: " + "\n".join(rec)
