#from __future__ import print_function
import time
from threading import Thread
import sys
import os

def inp():
	s = open("g:\\pylog.log", "w")
	s.write(raw_input())
	s.close()
	while 1:
		s = open("g:\\pylog2.log", "a")
		s.write(raw_input())
		s.close()

thread = Thread(target = inp, args = ())
thread.start()
start = time.time()
while time.time()-start < 10:
	print ("1" + "hey you an " * (10**2)  +" my")
	#print("hey\n")
	#sys.stdout.flush()
	#os.system("echo echo try")
	#sys.__stdout__.write("__stdout__\n")
	time.sleep(1.0)
	#sys.stdout.write("hey\n")
thread.join()