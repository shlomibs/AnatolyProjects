import sqlite3 as sql
from threading import Thread


def main():
	inputThread = Thread(target = InputProcessing, args = ())
	inputThread.start()

def InputProcessing():
	inp = raw_input()
	


if __name__ == "__main__":
	main()