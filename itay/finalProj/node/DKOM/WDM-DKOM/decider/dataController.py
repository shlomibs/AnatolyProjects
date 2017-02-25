from task import *

class DataController:
	#region constants
	SEND_CMD = 's'
	START_PROCESS_CMD = 'p'
	PROCESS_ENDED_CODE = 'e'
	PROCESS_DATA_CODE = 'd'
	QUERY_CODE = 'q'
	TASK_CODE = 't'
	DISPLAY_CODE = 'D' # display to admin <=> only if the admin is connected
	#endregion
	
	#region static vars
	tasks = []
	sendedTasks = [] # tasks that have been sended to other nodes via command from this machine
	#endregion

	#region "events"
	@staticmethod
	def OnCommunicationDataRecieved(data): # check what command recieved
		if data[0] == START_PROCESS_CMD: # start process
			StartProcess(data[1:])
		elif data[0] == PROCESS_DATA_CODE: # data recieved from task
			print DISPLAY_CODE + repr(data) # keep the CMD code
		elif data[0] == PROCESS_ENDED_CODE: # a sended task ended
			print DISPLAY_CODE + repr(data) # keep the CMD code
		elif data[0] == QUERY_CODE: # a sended query response
			print DISPLAY_CODE + repr(data) # keep the CMD code
		else:
			raise Exception("unknown command: '" + data[0] + "' full msg: " + data)

	@staticmethod
	def OnProcessDataRecieved(data):
		tsk = _FindTaskByData(data)
		SendData(tsk.sourceNodeId, tsk.sourceNodeTaskId, PROCESS_DATA_CODE + ",".join(data.split(",")[1:]))

	@staticmethod
	def OnProcessEnded(data):
		tsk = _FindTaskByData(data)
		SendData(tsk.sourceNodeId, tsk.sourceNodeTaskId, PROCESS_ENDED_CODE)
		tasks.remove(tsk)

	@staticmethod
	def OnQueryReceived(data):
		tsk = _FindTaskByData(data)
		SendData(tsk.sourceNodeId, tsk.sourceNodeTaskId, PROCESS_DATA_CODE + ",".join(data.split(",")[1:]))
		tasks.remove(tsk)
	#endregion

	@staticmethod
	def SendData(toId, nodeTaskId, data, toRepr=True):
		if toRepr:
			print SEND_CMD + toId + "," + nodeTaskId + "," + repr(data)
		else:
			print SEND_CMD + toId + "," + nodeTaskId + "," + data # if the data is already formatted

	@staticmethod
	def StartProcess(data):
		sourceNodeId, sourceNodeTaskId = data.split(",")[0:2]
		tsk = Task(TaskType.TASK, sourceNodeId, sourceNodeTaskId)
		tasks.append(tsk)
		print START_PROCESS_CMD + tsk.id + "," + repr(",".join(data.split(",")[2:]))

	@staticmethod
	def Query(data):
		fromId, nodeTaskId = data.split(",")[0:2] # take the first 2 vals (fromId, nodeTaskId, data)
		tsk = Task(TaskType.QUERY, fromId, nodeTaskId)
		tasks.append(tsk)
		print QUERY_CODE + tsk.id + "," + repr(data)

	@staticmethod
	def _FindTaskByData(data): # if the complexity will be too high then turn it to dictionary
		for t in tasks:
			if t.id == int(data.split(",")[0]):
				return t