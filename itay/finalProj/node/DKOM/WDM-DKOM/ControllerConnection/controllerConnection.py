#!/usr/bin/python
import sys
import traceback
from thread import start_new_thread
from socket import socket, AF_INET, SOCK_STREAM

nodeData = []
CLOSE_CODE = 'C'
CLIENTS_LIST_CODE = 'c'

def main():
	if(len(sys.argv) != 2):
		raise Exception("wrong parameters: " + str(sys.argv) + " , len: " + str(len(sys.argv)))
	port = int(sys.argv[1])
	entry = socket(AF_INET, SOCK_STREAM)
	entry.bind(("localhost", port))
	entry.listen(1)
	controllerSock, addr = entry.accept()
	start_new_thread(nodeReceivingLoop, (controllerSock,))
	controllerReceivingLoop(controllerSock)
	entry.close()
	exit(0)


def nodeReceivingLoop(controllerSock):
	try:
		while True:
			inp = raw_input() # input is repr'd
			controllerSock.send(inp + "\n")
	except Exception as e:
		print "node receiving exception: " + str(e)
		print "traceback: " + traceback.format_exc() # debug


def controllerReceivingLoop(controllerSock):
	recData = ""
	try:
		recData += controllerSock.recv(1024)
		while (recData != CLOSE_CODE + "\n"):
			if "\n" in recData:
				splt = recData.split("\n")
				recData = splt[-1] # unfinished msg, might be even "" (empty)
				for msg in splt[:-1]:
					if msg == CLOSE_CODE:
						recData = CLOSE_CODE +"\n"
						break 
					print msg # send to communicator
			if recData == CLOSE_CODE +"\n":
				break
			recData += controllerSock.recv(1024)
		controllerSock.close()
	except Exception as e:
		print "controller receiving exception: " + str(e)
		print "traceback: " + traceback.format_exc() # debug


if __name__ == "__main__":
	main()