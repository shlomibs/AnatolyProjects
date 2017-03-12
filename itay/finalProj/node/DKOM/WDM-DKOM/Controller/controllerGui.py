import wx
import wx.xrc
import shlex
from thread import start_new_thread

class ControllerGui():
	def __init__(self, taskManager):
		self.app = wx.App() 
		self.window = controllerWindow(None, taskManager, title = "wxPython Frame") 
		#self.panel = wx.Panel(self.window) 

	def Show(self): # must be in the main thread (blocking)
		self.window.Show(True) 
		self.app.MainLoop()

class controllerWindow (wx.Frame):
	###################################################################################
	## the next __init__ Python code generated with wxFormBuilder (version Jun 17 2015)
	## http://www.wxformbuilder.org/
	###################################################################################
	def __init__(self, parent, taskManager):
		self.taskManager = taskManager

		wx.Frame.__init__ (self, parent, id = wx.ID_ANY, title = u"controller", pos = wx.DefaultPosition, size = wx.Size(1000,700), style = wx.DEFAULT_FRAME_STYLE, name = u"controller")
		
		self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
		
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		
		cmdSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"command"), wx.HORIZONTAL)
		
		self.cmdTextControl = wx.TextCtrl(cmdSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
		self.cmdTextControl.SetMinSize(wx.Size(800,-1))
		
		cmdSizer.Add(self.cmdTextControl, 0, wx.ALL, 5)
		
		self.executeCmdButton = wx.Button(cmdSizer.GetStaticBox(), wx.ID_ANY, u"execute on all", wx.DefaultPosition, wx.DefaultSize, 0)
		cmdSizer.Add(self.executeCmdButton, 0, wx.ALL, 5)
		
		
		mainSizer.Add(cmdSizer, 1, wx.EXPAND, 5)
		
		querySizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"query"), wx.HORIZONTAL)
		
		self.qryTextControl = wx.TextCtrl(querySizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
		self.qryTextControl.SetMinSize(wx.Size(800,-1))
		
		querySizer.Add(self.qryTextControl, 0, wx.ALL, 5)
		
		self.qryExecuteButton = wx.Button(querySizer.GetStaticBox(), wx.ID_ANY, u"execute", wx.DefaultPosition, wx.DefaultSize, 0)
		querySizer.Add(self.qryExecuteButton, 0, wx.ALL, 5)
		
		
		mainSizer.Add(querySizer, 1, wx.EXPAND, 5)
		
		scriptSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"script"), wx.VERTICAL)
		
		executableSizer = wx.StaticBoxSizer(wx.StaticBox(scriptSizer.GetStaticBox(), wx.ID_ANY, u"executable"), wx.HORIZONTAL)
		
		self.executablePicker = wx.FilePickerCtrl(executableSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.*", wx.DefaultPosition, wx.Size(796,-1), wx.FLP_DEFAULT_STYLE)
		executableSizer.Add(self.executablePicker, 0, wx.ALL, 5)
		
		self.executeScriptButton = wx.Button(executableSizer.GetStaticBox(), wx.ID_ANY, u"execute", wx.DefaultPosition, wx.DefaultSize, 0)
		executableSizer.Add(self.executeScriptButton, 0, wx.ALL, 5)
		
		
		scriptSizer.Add(executableSizer, 1, wx.EXPAND, 5)
		
		argsFileSizer = wx.StaticBoxSizer(wx.StaticBox(scriptSizer.GetStaticBox(), wx.ID_ANY, u"args file"), wx.HORIZONTAL)
		
		self.argsFilePicker = wx.FilePickerCtrl(argsFileSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.*", wx.DefaultPosition, wx.Size(796,-1), wx.FLP_DEFAULT_STYLE)
		argsFileSizer.Add(self.argsFilePicker, 0, wx.ALL, 5)
		
		numOfNodesSizer = wx.StaticBoxSizer(wx.StaticBox(argsFileSizer.GetStaticBox(), wx.ID_ANY, u"connected nodes"), wx.VERTICAL)
		
		self.numOfNodesLabel = wx.StaticText(numOfNodesSizer.GetStaticBox(), wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0)
		self.numOfNodesLabel.Wrap(-1)
		numOfNodesSizer.Add(self.numOfNodesLabel, 0, wx.ALL, 5)
		
		
		argsFileSizer.Add(numOfNodesSizer, 1, wx.EXPAND, 5)
		
		
		scriptSizer.Add(argsFileSizer, 1, wx.EXPAND, 5)
		
		
		mainSizer.Add(scriptSizer, 1, wx.EXPAND, 5)
		
		self.outputTextControl = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY, wx.DefaultValidator, u"controller")
		self.outputTextControl.SetMinSize(wx.Size(1000,375))
		
		mainSizer.Add(self.outputTextControl, 0, wx.ALL|wx.EXPAND, 5)
		
		
		self.SetSizer(mainSizer)
		self.Layout()
		
		self.Centre(wx.BOTH)
		
		self.taskManager.SetOutput(self.outputTextControl.AppendText)

		# Connect Events
		self.Bind(wx.EVT_CLOSE, self.OnExit)
		self.executeCmdButton.Bind(wx.EVT_BUTTON, self.ExecuteCmd)
		self.qryExecuteButton.Bind(wx.EVT_BUTTON, self.ExecuteQuery)
		self.executeScriptButton.Bind(wx.EVT_BUTTON, self.ExecuteScript)
	
	#events:
	def OnExit(self, event):
		self.taskManager.OnExit()
	
	def ExecuteCmd(self, event):
		argv = shlex.split(str(self.cmdTextControl.GetValue()))
		args = "" if str(self.cmdTextControl.GetValue())[len(argv[0]):] == "" else str(self.cmdTextControl.GetValue())[len(argv[0]) + 1:]
		self.taskManager.ExecCmd(argv[0], args)
	
	def ExecuteQuery(self, event):
		self.taskManager.ExecQry(str(self.qryTextControl.GetValue()))
	
	def ExecuteScript(self, event):
		self.taskManager.ExecScript(str(self.executablePicker.GetPath()), str(self.argsFilePicker.GetPath()))