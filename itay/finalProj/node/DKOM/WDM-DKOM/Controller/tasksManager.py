import shlex
from task import *

class TasksManager:
	def __init__(self, outputFunc, sock):
		self.__outputFunc = outputFunc
		self.__sock = sock
		self.otherNodes = [] # nodes' ids
		self.currentTasks = {} # {nodeId:[tasks] ...}
		self.pendingTasks = []
	
	def SetOutput(self, func):
		self.__outputFunc = func

	def ExecQry(self, qry):
		task = Task(TaskType.QUERY, qry)
		for node in otherNodes:
			tsk = Task(task)
			currentTasks[node].append(tsk)
			self.__sock.send(tsk.GetNextCommand() + "\n")

	def ExecCmd(self, cmd, args): # command line like in cmd
		task = Task(TaskType.CMD, cmd, args)
		for node in otherNodes:
			tsk = Task(task)
			currentTasks[node].append(tsk)
			self.__sock.send(tsk.GetNextCommand() + "\n")
	
	def ExecScript(self, executablePath, argsFilePath):
		args = [arg.strip() for arg in open(argsFilePath).read().split("\n")] # strip to remove "\r" if exists
		tasks = [Task(TaskType.SCRIPT, executablePath, arg) for arg in args]
		for node in self.otherNodes:
			tsk = tasks.pop(0, None)
			if tsk == None:
				break;
			currentTasks[node].append(tsk)
			self.__sock.send(tsk.GetNextCommand() + "\n")
		if len(tasks) > 0:
			self.pendingTasks.append(tasks)

	def ExecFromBash(self, cmd): # cmd is string recieved from command line (bash) # FIN
		try:
			argv = shlex.split(cmd)
			args = "" if str(cmd)[len(argv[0]):] == "" else str(cmd)[len(argv[0]) + 1:]
			
			if argv[0].lower() in ["c", "cmd", "command"]:
				cmdArgv = shlex.split(args)
				cmdArgs = "" if str(args)[len(argv[0]):] == "" else str(args)[len(argv[0]) + 1:]
				self.ExecCmd(cmdArgv[0], cmdArgs)
			elif argv[0].lower() in ["q", "qry", "query"]:
				self.ExecQry(args)
			elif argv[0].lower() in ["s", "scrpt", "script"]:
				self.ExecScript(argv[1], argv[2])
			else:
				self.__outputFunc("illegal command\n")
		except:
			self.__outputFunc("illegal command syntax\n")

	def MessageReceived(self, msg):
		raise NotImplementedError()

	def OnExit(self):
		self.__sock.send(Task.CLOSE_CODE + "\n")
		sleep(0.1)
		self.__sock.close()
