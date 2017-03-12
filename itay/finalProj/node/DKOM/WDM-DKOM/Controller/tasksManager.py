from task import *

class TasksManager:
	def __init__(self, outputFunc, sock):
		self.__outpuFunc = outputFunc
		self.__sock = sock
		self.otherNodes = [] # nodes' ids
		self.currentTasks = {} # {nodeId:[tasks] ...}
		self.pendingTasks = []
	
	def SetOutput(self, func):
		self.__outpuFunc = func

	def ExecQry(self, qry):
		task = Task(TaskType.QUERY, qry)
		for node in otherNodes:
			tsk = Task(task)
			currentTasks[node].append(tsk)
			self.__sock.send(tsk.GetNextCommand())

	def ExecCmd(self, cmd, args): # command line like in cmd
		task = Task(TaskType.CMD, cmd, args)
		for node in otherNodes:
			tsk = Task(task)
			currentTasks[node].append(tsk)
			self.__sock.send(tsk.GetNextCommand())
	
	def ExecScript(self, executablePath, argsFilePath):
		args = [arg.strip() for arg in open(argsFilePath).read().split("\n")] # strip to remove "\r" if exists
		tasks = [Task(TaskType.SCRIPT, executablePath, arg) for arg in args]
		for node in self.otherNodes:
			tsk = tasks.pop(0, None)
			if tsk == None:
				break;
			currentTasks[node].append(tsk)
			self.__sock.send(tsk.GetNextCommand())
		if len(tasks) > 0:
			self.pendingTasks.append(tasks)

		raise NotImplementedError()

	def ExecFromBash(self, cmd): # cmd is string recieved from command line (bash)
		raise NotImplementedError()

	def MessageReceived(self, msg):
		raise NotImplementedError()

	def OnExit(self):
		raise NotImplementedError()
