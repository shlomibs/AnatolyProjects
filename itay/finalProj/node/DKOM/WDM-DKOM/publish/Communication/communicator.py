import sys
from time import sleep
from threading import Lock
from thread import start_new_thread
from uuid import getnode as getMacAsInt
import communicationUtils
from communication import Communication

import traceback

CLIENTS_LIST_CODE = 'c'
toSendQueue = []
lock = Lock() # lock for input queue
printLock = Lock()
CommunicatorQueueLog = open("comQueue.log", "w")
def main():
	global com
	ID = getMacAsInt() # returns the main mac address as a 48 bit integer
	if len(sys.argv) > 1: # for testing
		ID = int(sys.argv[1])
	com = Communication(ID, communicationUtils.defaultCommunicationKey())
	start_new_thread(inputLoop, ())
	start_new_thread(receivingLoop, ())
	sendingLoop()

def inputLoop():
	global lock, toSendQueue, CommunicatorQueueLog
	try:
		while True:
			splt = raw_input().split(",")
			msg = eval(",".join(splt[2:]))
			lock.acquire()
			CommunicatorQueueLog.write("inserted: " + splt[0] + ", " + msg[0] + splt[1] + "," + msg[1:] + "\n")
			CommunicatorQueueLog.flush()
			toSendQueue.append((splt[0], msg[0] + splt[1] + "," + msg[1:])) # according to format -> CODE + nodeTaskId + "," + data
			lock.release()
	except Exception as e:
		f = open(sys.argv[0]+".log", "a")
		f.write("exception: " + str(e) + "\n")
		f.write("trcbk: " + traceback.format_exc() + "\n")
		f.close()
		print "exception: " + str(e)
		print "trcbk: " + traceback.format_exc() # for debug
		raise e

def receivingLoop():
	global com
	try:
		while True:
			msgs = com.getReceivedMessages()
			for id, msg in msgs:
				splt = msg[1:].split(",")
				data = ",".join(splt[1:])
				printLock.acquire()
				print repr(msg[0] + str(id) + "," + splt[0] + "," + data) # msg = CODE + nodeTaskId + "," + data
				printLock.release()
			sleep(0.01)
	except Exception as e:
		f = open(sys.argv[0]+".log", "a")
		f.write("exception: " + str(e) + "\n")
		f.write("trcbk: " + traceback.format_exc() + "\n")
		f.close()
		print "exception: " + str(e)
		print "trcbk: " + traceback.format_exc() # for debug
		raise e

def sendingLoop():
	global lock, toSendQueue, com, CommunicatorQueueLog
	com.refreshContacts()
	i = 0
	try:
		while True:
			i += 1
			if len(toSendQueue) == 0:
				if(i > 10*100): # approximatly 10 seconds
					printLock.acquire()
					print repr(CLIENTS_LIST_CODE + repr(com.getContacts()))
					printLock.release()
					i = 0
					com.refreshContacts()
				else:
					sleep(0.01)
				continue
			while(len(toSendQueue) > 0):
				lock.acquire()
				toId, data = toSendQueue.pop(0)
				CommunicatorQueueLog.write("removed: " + toId + ", " + data + "\n")
				CommunicatorQueueLog.flush()
				lock.release()
				com.send(data, toId)
	except Exception as e:
		f = open(sys.argv[0]+".log", "a")
		f.write("exception: " + str(e) + "\n")
		f.write("trcbk: " + traceback.format_exc() + "\n")
		f.close()
		print "exception: " + str(e)
		print "trcbk: " + traceback.format_exc() # for debug
		raise e

if __name__ == "__main__":
	main()