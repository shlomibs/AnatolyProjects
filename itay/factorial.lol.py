#!/usr/env/python

fact = lambda x: x*a(x-1) if x!=1 else 1

if __name__ == "__main__":
	print str(fact(input("number:")))
