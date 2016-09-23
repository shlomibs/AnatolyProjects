#!/usr/bin/python
import sys

fact = lambda x: x*fact(x-1) if x!=1 else 1

if __name__ == "__main__":
	if len(sys.argv) == 1:
		input("number:")
		sys.setrecursionlimit(inp + 2)
		print str(fact(inp))
	else:
		sys.setrecursionlimit(int(sys.argv[1]) + 2)
		print str(fact(int(sys.argv[1])))
