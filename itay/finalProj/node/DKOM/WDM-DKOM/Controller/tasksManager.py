
class TasksManager:
	def __init__(self, OutputFunc):
		self.OutpuFunc = OutputFunc
		self.tasks = [] # (
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