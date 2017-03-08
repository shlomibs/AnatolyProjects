#!/usr/bin/python
import sys
from time import sleep
from threading import Lock
from thread import start_new_thread
from socket import socket #, AF_INET, SOCK_STREAM
from tasksManager import TasksManager

sys.path.append('../communication/')
from communicationUtils import isPortTaken


printLock = Lock()
taskManager = 0 # temp just for making it a global var
def main():
	try:
		sock = socket() # AF_INET, SOCK_STREAM
		sock.connect(FindFreePort)
	except Exception as e:
		print "cannot connect: " + str(e)
	start_new_thread(nodeReceivingLoop, (sock,))
	if sys.argv == "bash.py": # executing bash.py or python bash.py or python -u bash.py
		bash()
	else:
		gui()


shutdown = False
nodeData = ""
def nodeReceivingLoop(sock):
	global nodeData
	while not shutdown:
		try:
			nodeData += sock.recv(1024)
			nodeDataProcessing() # using nodeData
		except Exception as e:
			print "exception: " + str(e)
			break


def nodeDataProcessing():
	global nodeData, taskManager
	if "\n" not in nodeData: # data not complete
		return
	data = nodeData.split("\n")
	nodeData = data[-1] # can be empty string ("")
	data = data[0:-1]

	for msg in data:
		decMsg = eval(data)
		taskManager.MessageReceived(msg)
	raise NotImplementedError()

def BashOutput(msg):
	global printLock
	printLock.aquire()
	print msg
	printLock.release()

def bash():
	global taskManager
	taskManager = TasksManager(BashOutput)
	nodesIds = GetOtherNodesIds()
	print "other nodes: " + nodesIds
	inp = raw_input(">> ")
	# declare format ...

def gui():
	global taskManager
	gui = ControllerGui()
	gui.show()
	# start a gui with wx
	raise NotImplementedError()

def GetOtherNodesIds():
	raise NotImplementedError()

if __name__ == "__main__":
	main()