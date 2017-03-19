import shlex
from time import sleep
from task import *

class TasksManager:
	def __init__(self, sock, outputFunc = lambda x: None, numOfNodesOutputFunc = lambda num: None):
		self.__sock = sock
		self.__outputFunc = outputFunc
		self.__numOfNodesOutputFunc = numOfNodesOutputFunc
		self.__nextMissionId = 1
		self.otherNodes = [] # nodes' ids
		self.currentTasks = {} # {nodeId:[tasks] ...}
		self.pendingTasks = []
	
	def SetOutput(self, func):
		self.__outputFunc = func
		
	def SetNumNodesOutput(self, func):
		self.__numOfNodesOutputFunc = func

	def ExecQry(self, qry):
		task = Task(TaskType.QUERY, qry)
		for node in self.otherNodes:
			tsk = task.Copy()
			self.currentTasks[node].append(tsk)
			cmnd = tsk.GetNextCommand()
			self.__sock.send(node + "," + cmnd + "\n")
			print "sended: " + node + "," + cmnd

	def ExecCmd(self, cmd, args): # command line like in cmd
		task = Task(TaskType.CMD, cmd, args)
		for node in self.otherNodes:
			tsk = task.Copy()
			self.currentTasks[node].append(tsk)
			cmnd = tsk.GetNextCommand()
			self.__sock.send(node + "," + cmnd + "\n")
			print "sended: " + node + "," + cmnd
	
	def ExecScript(self, executablePath, argsFilePath):
		args = [arg.strip() for arg in open(argsFilePath).read().split("\n")] # strip to remove "\r" if exists
		tasks = [Task(TaskType.SCRIPT, executablePath, arg, self.__nextMissionId) for arg in args]
		self.__nextMissionId += 1
		for node in self.otherNodes:
			if len(tasks) == 0:
				break;
			tsk = tasks.pop(0)
			self.currentTasks[node].append(tsk)
			cmnd = tsk.GetNextCommand()
			self.__sock.send(node + "," + cmnd + "\n")
			print "sended: " + node + "," + cmnd
		if len(tasks) > 0:
			self.pendingTasks += tasks

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
			elif argv[0].lower() in ["n", "nodes"]:
				self.__outputFunc(str(len(self.otherNodes)) + "\n")
			else:
				self.__outputFunc("illegal command\n")
		except:
			self.__outputFunc("illegal command syntax\n")

	def MessageReceived(self, msg):
		if msg[0] == Task.CLIENTS_LIST_CODE:
			self.otherNodes = eval(msg[1:])
			self.__numOfNodesOutputFunc(str(len(self.otherNodes)))
			disconnected = [n for n in self.currentTasks.keys() if n not in self.otherNodes]
			new = [n for n in self.otherNodes if n not in self.currentTasks.keys()]
			for node in disconnected:
				for tsk in self.currentTasks[node]:
					if tsk.type == TaskType.SCRIPT:
						tsk.Restart()
						self.pendingTasks.append(tsk)
				del self.currentTasks[node]
			tasksById = {}
			for tsk in self.pendingTasks: # prepare
				if tsk.missionId not in tasksById.keys():
					tasksById[tsk.missionId] = []
				tasksById[tsk.missionId].append(tsk)
			for node in new:
				self.currentTasks[node] = []
				for mission in tasksById.keys():
					matchingTasks = tasksById[mission]
					if len(matchingTasks) > 0:
						tsk = matchingTasks.pop(0)
						self.currentTasks[node].append(tsk)
						cmnd = tsk.GetNextCommand()
						self.__sock.send(node + "," + cmnd + "\n")
						print "sended: " + node + "," + cmnd
		elif msg[0] == PROCESS_DATA_CODE: # data recieved from task
			splt = msg[1:].split(",")
			tsk = next(tsk for tsk in self.currentTasks[splt[0]] if tsk.GetActiveCommandId() == int(splt[1])) # find the first that matches the criteria
			self.__outputFunc(tsk.name + ": " + ",".join(splt[2:]))
		elif msg[0] == PROCESS_ENDED_CODE: # a sended task ended
			splt = msg[1:].split(",")
			tsk = next(tsk for tsk in self.currentTasks[splt[0]] if tsk.GetActiveCommandId() == int(splt[1])) # find the first that matches the criteria
			nextCmd = tsk.GetNextCommand()
			if nextCmd != None:
				self.__sock.send(splt[0] + "," + nextCmd + "\n")
			else: # None = task finished
				newTsk = next((t for t in self.pendingTasks if t.missionId == tsk.missionId), None)
				if newTsk != None:
					self.pendingTasks.remove(newTsk)
					self.currentTasks[splt[0]].append(newTsk)
				cmnd = tsk.GetNextCommand()
				self.__sock.send(node + "," + cmnd + "\n")
				print "sended: " + node + "," + cmnd
		elif msg[0] == QUERY_RESPONSE_CODE: # a sended query response
			splt = msg[1:].split(",")
			tsk = next(tsk for tsk in self.currentTasks[splt[0]] if tsk.GetActiveCommandId() == int(splt[1])) # find the first that matches the criteria
			self.currentTasks[splt[0]].remove(tsk)
			self.__outputFunc(tsk.name + ": " + ",".join(splt[2:]))
		else:
			raise Exception("unknown command: '" + msg[0] + "' full msg: " + msg)

	def OnExit(self):
		self.__sock.send(Task.CLOSE_CODE + "\n")
		sleep(0.1)
		self.__sock.close()
