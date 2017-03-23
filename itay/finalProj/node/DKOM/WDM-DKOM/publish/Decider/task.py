

class TaskType:
	QUERY = 0
	TASK = 1

class Task:
	nextId = 0 # static var
	def __init__(self, taskType, sourceNodeId, sourceNodeTaskId):
		self.type = taskType
		self.id = Task.nextId
		self.sourceNodeId = sourceNodeId
		self.sourceNodeTaskId = sourceNodeTaskId
		Task.nextId += 1
		if Task.nextId >= 2**16:
			Task.nextId = 0
