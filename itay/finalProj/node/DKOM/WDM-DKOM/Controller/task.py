
class TaskType:
	QUERY = 0
	CMD = 1
	SCRIPT = 2


class Task:
	#region constants
	SEND_CMD = 's'
	START_PROCESS_CMD = 'p'
	QUERY_CMD = 'q'
	PROCESS_ENDED_CODE = 'e'
	PROCESS_DATA_CODE = 'd'
	QUERY_RESPONSE_CODE = 'Q'
	TASK_CODE = 't'
	WRITE_FILE_CMD = 'w'
	CLIENTS_LIST_CODE = 'c'
	#endregion

	#region static vars
	nextId = 0
	#endregion

	def __init__(self, type, cmd, args = ""):
		self.name = cmd + " " + args + ": "
		self.type = type
		self.__lastCommandId = -1 # illegal id
		#self.commands = []
		if self.type == TaskType.CMD:
			self.commands = [(nextId, Task.TASK_CODE + str(nextId) + "," + cmd + "," + args)] # [(id, command)]
		elif self.type == TaskType.QUERY:
			self.commands = [(nextId, Task.QUERY_CMD + str(nextId) + "," + cmd)] # [(id, command)]
		else: # self.type == TaskType.SCRIPT
			content = open(cmd, 'rb').read() # cmd is the script 
			command = cmd.split("\\")[-1].split("/")[-1]
			# next make python unbuffered if it is a python script
			command, args = "python", "-u " + command + " " + args if len(command.split(".")) > 1 and command.split(".")[-1].lower() in ["py", "pyw", "pyc"] else command, args
			self.commands = [(nextId, Task.WRITE_FILE_CMD + str(nextId) + "," + cmd.split("\\")[-1].split("/")[-1] + "," + content),
					(nextId + 1, Task.TASK_CODE + str(nextId + 1) + "," + command + "," + args)] # [(id, command), (id, command)]
			nextId += 1
		nextId += 1

	def __init__(self, otherTask): # copy constructor
		self.name = otherTask.name
		self.type = otherTask.type
		self.__lastCommandId = -1
		self.commands = list(otherTask.commands) # same taskId!

	def __str__(self):
		return self.name

	def GetNextCommand(self):
		if len(self.commands) == 0:
			return None
		id, cmd = self.commands.pop(0)
		self.__lastCommandId = id
		return cmd

	def GetActiveCommandId(self):
		return self.__lastCommandId
