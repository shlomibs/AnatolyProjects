import sqlite3 as sql

class DatabaseHandler:
	def __init__(self, filePath):
		self._dbFile = filePath
		self._isExecutingQuery = False # precaution
	
	def executeQuery(self, qry):
		if self._isExecutingQuery: # the precaution
			raise Exception("still running a query")
			#return
		self._isExecutingQuery = True
		try:
			connection = sql.connect(self._dbFile) # creates a db if it doesnt exists
			cursor = connection.cursor()
			
			cursor.execute(qry)
			#data = []
			#if "SELECT" in qry.upper().split(" "): # if get data
			data = cursor.fetchall() # maybe not only for select
			connection.commit() # for beening safe
			connection.close();
			self._isExecutingQuery = False
			return data
		except Exception as e: # sql.Error, e:
			self._isExecutingQuery = False
			return e
			#print str(e)
			#print "Error %s:" % e.args[0]
			#raise e