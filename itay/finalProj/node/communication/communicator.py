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
	global lock, toSendQueue
	while True:
		splt = raw_input().split(",")
		msg = eval(",".join(splt[2:]))
		lock.acquire()
		toSendQueue.append((splt[0], msg[0] + splt[1] + "," + msg[1:])) # according to format -> CODE + nodeTaskId + "," + data
		lock.release()

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
		#print "exception: " + str(e)
		#print "trcbk: " + traceback.format_exc() # for debug
		raise e

def sendingLoop():
	global lock, toSendQueue, com
	com.refreshContacts()
	i = 0
	while True:
		i += 1
		if i == 50: # give 0.5 second to receive the info
			printLock.acquire()
			print repr(CLIENTS_LIST_CODE + repr(com.getContacts()))
			printLock.release()
		if len(toSendQueue) == 0:
			if(i > 10*100): # approximatly 10 secomds
				i = 0
				com.refreshContacts()
			else:
				sleep(0.01)
			continue
		while(len(toSendQueue) > 0):
			lock.acquire()
			toId, data = toSendQueue.pop()
			lock.release()
			com.send(data, toId)

if __name__ == "__main__":
	main()