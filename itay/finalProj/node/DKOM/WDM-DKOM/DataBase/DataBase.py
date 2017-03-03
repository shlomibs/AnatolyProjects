#!/usr/bin/python
import sqlite3 as sql
import sys
from databaseHandler import DatabaseHandler

def main():
	if len(sys.argv) != 2:
		print "incorrect args"
		sys.exit(-1) # error
	dbHandler = DatabaseHandler(sys.argv[1])
	while True:
		inp = eval(raw_input()) # get query
		ret = dbHandler.executeQuery(inp) # execute
		print repr(ret) # return result via stdout

if __name__ == "__main__":
	main()