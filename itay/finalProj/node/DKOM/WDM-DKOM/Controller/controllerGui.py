import wx
from thread import start_new_thread

class ControllerGui():
	def __init__(self):
		self.app = wx.App() 
		self.window = wx.Frame(None, title = "wxPython Frame", size = (300,200)) 
		self.panel = wx.Panel(self.window) 

	def Show(self): # must be in the main thread
		self.window.Show(True) 
		self.app.MainLoop()

