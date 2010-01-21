'''
Created on 01/12/2009

@author: lrg
'''

import wx
from MainFrame import MainFrame
from ExperimentServerTester import *

# Change "oneMinutePython" with the name of your application

class MainApp(wx.App):
    
    def __init__(self, parent, mst):
        self.mst = mst
        wx.App.__init__(self, parent)
    
    def OnInit(self):
        self.mFrame = MainFrame(None, self.mst)
        self.mst.set_window(self.mFrame)
        self.mFrame.Show()
        self.SetTopWindow(self.mFrame)
        return True

mst = ExperimentServerTester()
app = MainApp(0, mst)
app.MainLoop()
