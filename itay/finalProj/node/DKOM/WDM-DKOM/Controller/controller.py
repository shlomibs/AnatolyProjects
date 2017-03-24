#!/usr/bin/python
if __name__ == "__main__":
	print "initiallizing . . ." # before because scapy
import os, sys
from time import sleep
from random import randint
from threading import Lock
from thread import start_new_thread
import traceback
from scapy.all import *
from socket import socket, AF_INET, SOCK_DGRAM
from tasksManager import * # TasksManager
from controllerGui import ControllerGui

sys.path.append('../Communication/')
from communicationUtils import IsPortTaken, defaultCommunicationKey
from encoder import Encoder

printLock = Lock()
taskManager = 0 # temp just for making it a global var 
def main(): # FIN
	try:
		port = FindFreePort()
		try:
			#trigSock = socket(AF_INET, SOCK_DGRAM) # UDP
			encoder = Encoder(defaultCommunicationKey())
			#dport = int(encoder.decrypt(open("../Communication/config.cfg").read()))
			dport = int(encoder.decrypt(open("../config.cfg").read())) # the active directory of other modules should be the major application directory (manager's dir)
			while port == dport:
				port = FindFreePort()
			triggerMsg = "-1,0,m," + encoder.encrypt(Task.DISPLAY_CODE + str(port))
			print "trying to connect via port " + str(port) + " |msg: " + triggerMsg
			EOM = "-1,1,m,<EOF>"
			toSend = []
			#for mip in GetMachineInternalIps():#ips:
			toSend.append(IP(dst="127.0.0.1")/UDP(sport=6878, dport=dport)/triggerMsg) # 6878 = random port
			toSend.append(IP(dst="127.0.0.1")/UDP(sport=6878, dport=dport)/EOM) # end message
			send(toSend)#, verbose=False)
			sleep(2) # wait for the server to start
		except Exception as e:
			print "udp trigger exception: " + str(e)
			print "traceback: " + traceback.format_exc() # debug
			exit(-1)
		sock = socket() # AF_INET, SOCK_STREAM # TCP
		sock.connect(("127.0.0.1", port))
	except Exception as e:
		print "cannot connect: " + str(e)
		print "traceback: " + traceback.format_exc() # debug
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
			if str(e) == "[Errno 9] Bad file descriptor":
				exit(0) # ended session
			print "exception: " + str(e)
			print "traceback: " + traceback.format_exc() # debug
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
		print "received: " + decMsg
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
	taskManager.OnExit()
	BashOutput("exited\n")

#endregion

def Gui(sock): # FIN
	global taskManager
	taskManager = TasksManager(sock) # no output functions, will be changed in ControllerGui
	gui = ControllerGui(taskManager)
	gui.Show() # must be on the main thread

def FindFreePort(): # FIN
	port = randint(2048, 2**16 - 1)
	while IsPortTaken(port):
		port = (port + 1) % 2**16
	return port

if __name__ == "__main__":
	main()
