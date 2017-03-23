#!/usr/bin/python
import sqlite3 as sql
import sys
from databaseHandler import DatabaseHandler
import traceback

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
	try:
		main()
	except Exception as e:
		with open(sys.argv[0] + ".log", "a") as f:
			f.write("exception: " + str(e) + "\ntraceback: " + traceback.format_exc())
		print "exception: " + str(e)
		print "traceback: " + traceback.format_exc() # debug