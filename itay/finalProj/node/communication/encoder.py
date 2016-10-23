#!/usr/bin/python



class Encoder:
	def __init__(self, key):
		# key = string
		self.key = key
		
	def decode(self, QuerriesAndTasks): # FIN
		if(type(QuerriesAndTasks) == type(list()))
			retLst = []
			for item in QuerriesAndTasks:
				retLst.append(self.__decode(item))
			return retLst
		return self.__decode(QandT) # if single item

	def __decode(QuerryOrThread):
		raise("Not implemented execption")
		
	def encodeQuerry(Querry):
		raise("Not implemented execption")
		
	def encodeTask(Task):
		raise("Not implemented execption")
