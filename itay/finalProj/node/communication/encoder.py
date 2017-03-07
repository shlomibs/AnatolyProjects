#!/usr/bin/python
from base64 import b64encode, b64decode

class Encoder: # encryption with xor (list of values) and base64
	def __init__(self, key):
		# key = string
		self.__keys = []
		while key != 0:
			self.__keys.append(int(key%256))
			key /= 256

	def decrypt(self, msgs): # in format [(ID, msg)...]
		if(type(msgs) == type(list())):
			retLst = []
			for item in msgs:
				retLst.append(item[0], self.__decrypt(item[1]))
			return retLst
		return self.__decrypt(msgs) # if single item

	def __decrypt(msg): # type(msg) = string
		notBase64 = b64decode(msg)
		newMsg = ""
		i = 0
		for ch in notBase64:
			newMsg += chr(ord(ch) ^ self.__keys[i % len(self.__keys)])
			i += 1
		return newMsg
		
	def encrypt(msg): # type(msg) = string
		newMsg = ""
		i = 0
		for ch in msg[1]:
			newMsg += chr(ord(ch) ^ self.__keys[i % len(self.__keys)])
			i += 1
		return b64encode(newMsg) # base 64 to disable some spacial characters
