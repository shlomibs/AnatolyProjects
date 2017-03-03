
class TasksManager:
	def __init__(self, OutputFunc):
		self.OutpuFunc = OutputFunc

	def StartTask(self, cmd): # cmd is string recieved from command line
		raise NotImplementedError()

	def StartTask(self, cmd, argsFileName):
		raise NotImplementedError()

	def Query(self, query):
		raise NotImplementedError()

	def MessageReceived(self, msg):
		raise NotImplementedError()