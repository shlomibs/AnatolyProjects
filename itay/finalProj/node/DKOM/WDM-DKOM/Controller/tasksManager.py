
class TasksManager:
	#region constants
	SEND_CMD = 's'
	START_PROCESS_CMD = 'p'
	QUERY_CMD = 'q'
	PROCESS_ENDED_CODE = 'e'
	PROCESS_DATA_CODE = 'd'
	QUERY_RESPONSE_CODE = 'Q'
	TASK_CODE = 't'
	DISPLAY_CODE = 'D' # display to admin <=> only if the admin is connected
	WRITE_FILE_CMD = 'w'
	CLIENTS_LIST_CODE = 'c'
	#endregion

	def __init__(self, OutputFunc):
		self.OutpuFunc = OutputFunc
		self.tasks = [] # [(taskId, ... # continue
		self.nextTaskId = 1
		
	def ExecCmd(self, cmd): # command line like in cmd
		raise NotImplementedError()
	
	def ExecQry(self, qry):
		raise NotImplementedError()
	
	def ExecScript(self, executablePath, argsFilePath):
		raise NotImplementedError()

	def StartTask(self, cmd): # cmd is string recieved from command line
		raise NotImplementedError()

	def MessageReceived(self, msg):
		raise NotImplementedError()

	def OnExit(self):
		raise NotImplementedError()