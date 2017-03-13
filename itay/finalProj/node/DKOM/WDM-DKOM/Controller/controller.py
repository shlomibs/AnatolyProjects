#!/usr/bin/python
import sys
from time import sleep
from random import randint
from threading import Lock
from thread import start_new_thread
from socket import socket, AF_INET, SOCK_DGRAM
from tasksManager import * # TasksManager

sys.path.append('../communication/')
from communicationUtils import IsPortTaken, defaultCommunicationKey
from encoder import Encoder

printLock = Lock()
taskManager = 0 # temp just for making it a global var 
def main(): # FIN
	try:
		port = FindFreePort()
		try:
			trigSock = socket(AF_INET, SOCK_DGRAM) # UDP
			encoder = Encoder(defaultCommunicationKey())
			triggerMsg = "-1,0,m," + encoder.encrypt(Task.DISPLAY_CODE + str(port))
			EOM = "-1,1,m,<EOF>"
			for i in xrange(1, 2**16):
				trigSock.sendto(triggerMsg, ("127.0.0.1", i))
				trigSock.sendto(EOM, ("127.0.0.1", i))
			sleep(1) # wait for the server to start
		except Exception as e:
			print "udp trigger exception: " + str(e)
			exit(-1)
		sock = socket() # AF_INET, SOCK_STREAM # TCP
		sock.connect(port)
	except Exception as e:
		print "cannot connect: " + str(e)
		exit(-1)
	start_new_thread(NodeReceivingLoop, (sock,))
	if "bash.py" in sys.argv[0]: # executing bash.py or python bash.py or python -u bash.py
		Bash(sock)
	else:
		Gui(sock)

shutdown = False
nodeData = ""
def NodeReceivingLoop(sock): # FIN
	global nodeData
	while not shutdown:
		try:
			nodeData += sock.recv(1024)
			NodeDataProcessing() # using nodeData
		except Exception as e:
			print "exception: " + str(e)
			break

def NodeDataProcessing():
	global nodeData, taskManager
	if "\n" not in nodeData: # data not complete
		return
	data = nodeData.split("\n")
	nodeData = data[-1] # can be empty string ("")
	data = data[0:-1]

	for msg in data:
		decMsg = eval(msg)
		taskManager.MessageReceived(decMsg)

#region bash

bashHelp ="""
commands:
cmd <command> [arg1 [arg2 [arg3...]]]
query <query-syntax (repr'd = with \r,\n,\t... and surrounded by '' or "" by the format)>
script <executable-path> <args-file-path>
nodes
"""[1:] # remove the first \n

def BashOutput(msg): # FIN
	global printLock
	printLock.acquire()
	print msg,
	printLock.release()

def Bash(sock): # FIN
	global taskManager
	BashOutput(bashHelp)
	BashOutput("initializing . . .\n")
	taskManager = TasksManager(BashOutput, sock)
	BashOutput("initialized\n")
	inp = ""
	while inp.lower() not in ["exit", "quit", "escape"]:
		inp = raw_input()
		taskManager.ExecFromBash(inp)
	BashOutput("exited\n")

#endregion

def Gui(sock): # FIN
	global taskManager
	taskManager = TasksManager(sock) # no output functions, will be changed in ControllerGui
	gui = ControllerGui(taskManager)
	gui.show() # must be on the main thread

def FindFreePort(): # FIN
	port = randint(2048, 2**16 - 1)
	while IsPortTaken(port):
		port = (port + 1) % 2**16
	return port

if __name__ == "__main__":
	main()