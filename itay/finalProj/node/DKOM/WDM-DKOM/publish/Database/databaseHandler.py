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
			conn = sql.connect(self._dbFile) # creates a db if it doesnt exists
			cursor = con.cursor()
			
			cursor.execute(qry)
			data = []
			if "SELECT" in qry.upper().split(" "): # if get data
				data = cur.fetchall()
				conn.commit() # for beening safe
			else: # no need to return data
				conn.commit() # for beening safe
			conn.close();
			self._isExecutingQuery = False
			return data
		except sql.Error, e:
			print "Error %s:" % e.args[0]
			raise e