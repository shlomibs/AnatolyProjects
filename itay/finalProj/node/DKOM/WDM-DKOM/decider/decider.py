#!/usr/bin/python
import sys
from time import sleep
from thread import start_new_thread
from threading import Lock
from dataController import *

cmds = [] # commands recieved via stdin
shutdown = False
lock = Lock()

def main():
	start_new_thread(ActionLoop, ())
	ReceivingLoop()
	return -1 # temp

def ReceivingLoop():
	global lock, shutdown
	while not shutdown:
		inp = raw_input()
		lock.aquire()
		cmd.append(inp)
		lock.release()

def ActionLoop():
	global lock, shutdown
	while not shutdown:
		if len(cmds) == 0: # no command
			sleep(0.01)
			continue
		lock.aquire()
		data = cmds.pop(0)
		lock.release()
		if data[0] == DataController.SEND_CMD: # data recieved from another node
			OnCommunicationDataRecieved(data[1:])
		elif data[0] == DataController.PROCESS_DATA_CODE: # data recieved from process
			DataController.OnProcessDataReceived(data[1:])
		elif data[0] == DataController.PROCESS_ENDED_CODE: # process ended
			DataController.OnProcessEnded(data[1:])
		elif data[0] == DataController.QUERY_RESPONSE_CODE: # query response
			DataController.OnQueryReceived(data[1:])
		else:
			raise Exception("unknown command: '" + data[0] + "' full msg: " + data)




if __name__ == "__main__":
	main()