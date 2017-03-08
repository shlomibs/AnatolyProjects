import sys
import communicationUtils
from communication import Communication
from uuid import getnode as getMacAsInt

def main():
	ID = getMacAsInt() # returns the main mac address as a 48 bit integer
	com = Communication(ID, communicationUtils.defaultCommunicationKey())



if __name__ == "__main__":
	main()