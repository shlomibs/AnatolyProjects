

class TaskType:
	QUERY = 0
	TASK = 1

class Task:

	nextId = 0 # static var

	def __init__(self, taskType, sourceNodeId, sourceNodeTaskId):
		self.type = taskType
		self.id = nextId
		self.sourceNodeId = sourceNodeId
		self.sourceNodeTaskId = sourceNodeTaskId
		nextId += 1
		if nextId >= 2**16:
			nextId = 0
	#def
