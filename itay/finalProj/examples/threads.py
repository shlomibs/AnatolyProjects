#!/usr/bin/python
import time
import threading

def myFunc(arg1, arg2):
	while True:
		print arg1
		time.sleep(arg2)


if __name__ == "__main__":
	arg1, arg2 = ">>>", 1
	t = threading.Thread(target=myFunc, args = (arg1, arg2))
	t.daemon = True
	t.start()
	inp = raw_input("")
	while inp != "exit":
		inp = raw_input("")
	print "slp for 3 sec..."
	t2 = threading.Thread(target=time.sleep, args = (3,))
	t2.start()
	t2.join() # wait for it

