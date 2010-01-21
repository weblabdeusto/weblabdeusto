#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 26/11/2009

@author: Luis Rodr�guez
'''


import xmlrpclib
import random
import base64
import time

from threaded import *

from results import *


class IExperimentServerTesterNotifier(object):
    
    def ConnectNotification(self, addr, port, result):
        pass
    
    def StartExperimentNotification(self, result):
        pass
    
    def SendCommandNotification(self, cmd, result):
        pass
    
    def SendFileNotification(self, file_content, file_info, result):
        pass
    
    def DisposeNotification(self, result):
        pass
    
    def DisconnectNotification(self):
        pass
        
    

class ExperimentServerTester(object):
    '''
    Contains main Experiment Server Tester non-gui functionality.
    '''


    def __init__(self, experiment_server_tester_notifier=IExperimentServerTesterNotifier()):
        """
        Constructor
        @param experiment_server_tester_notifier An object which implements 
        IExperimentServerTesterNotifier interface, or None.
        """
        self.server = None
        self.mNotifier = experiment_server_tester_notifier
        self.mWindow = None
        
    def _set_notifier(self, notifier):
        self.mNotifier = notifier
        
    def set_window(self, window):
        self.mWindow = window
        
    Notifier = property(lambda self: self.mNotifier, _set_notifier)
       
    def connect(self, addr, port, uri):
        try:
            if self.is_connected(): self.disconnect()
            constr = "http://%s:%s/%s" % (addr, port, uri)
            print "Connecting"
            self.server = xmlrpclib.Server(constr)
            print "Server created."
            rndstr = str(random.random())
            result = self.test_me(rndstr)
            if result != rndstr:
                raise Exception("Connection not working as expected.")
            wx.PostEvent(self.mWindow, ResultEvent(
                lambda: self.mNotifier.ConnectNotification(addr, port, True) 
                ))
        except Exception, e:
            del self.server
            self.server = None
            wx.PostEvent(self.mWindow, ResultEvent(
                lambda: self.mNotifier.ConnectNotification(addr, port, False) 
                ))
            return e
        
    @threaded()
    def connect_t(self, addr, port, uri):
        return self.connect(addr, port, uri)
        
    def start_experiment(self):
        result = self.server.Util.start_experiment()
        wx.PostEvent(self.mWindow, ResultEvent(
                lambda: self.mNotifier.StartExperimentNotification(result)
                ))
        return result
    
    @threaded()
    def start_experiment_t(self):
        return self.start_experiment()
        
    def send_command(self, command):
        result = self.server.Util.send_command_to_device(command)
        wx.PostEvent(self.mWindow, ResultEvent(
                lambda: self.mNotifier.SendCommandNotification(command, result)
                ))
        return result
    
    @threaded()
    def send_command_t(self, command):
        return self.send_command(command)
    
    
    def send_file(self, file_content, file_info):
        file_content = base64.b64encode(file_content)
        result = self.server.Util.send_file_to_device(file_content, file_info)
        wx.PostEvent(self.mWindow, ResultEvent(
                lambda: self.mNotifier.SendFileNotification(file_content, file_info, result)
                ))
        return result
    
    @threaded()
    def send_file_t(self, file_content, file_info):
        return self.send_file(file_content, file_info)
        

    def dispose(self):
        result = self.server.Util.dispose()
        wx.PostEvent(self.mWindow, ResultEvent(
                lambda: self.mNotifier.DisposeNotification(result)
                ))
        return result
    
    @threaded()
    def dispose_t(self):
        return self.dispose()
        

    def disconnect(self):
        del self.server
        self.server = None
        self.mNotifier.DisconnectNotification()
        
    @threaded()
    def disconnect_t(self):
        return self.disconnect()
        

    def test_me(self, msg):
        return self.server.Util.test_me(msg)
        
    @threaded()
    def test_me_t(self, msg):
        return self.test_me(msg)
        
    def is_connected(self):
        return self.server is not None
  
    def send_file_by_path(self, path, info=""):
        content = file(path, u"r").read()
        result = self.send_file(content, info)
        
    @threaded()
    def send_file_by_path_t(self, path, info=""):
        return self.send_file_by_path(path, info)
        
    @threaded()
    def msg_box(self, msg, title = "Info"):
        __import__("wx").MessageBox(msg, title)
    
    def run_script(self, script_file):
        loc = dict()
        loc["connect"] = self.connect
        loc["send_file"] = self.send_file_by_path
        loc["send_command"] = self.send_command
        loc["dispose"] = self.dispose
        loc["start_experiment"] = self.start_experiment
        loc["test_me"] = self.test_me
        loc["disconnect"] = self.disconnect
        loc["msg_box"] = self.msg_box
        execfile(script_file, globals(), loc)
        #if(self.is_connected()): pass
            #self.disconnect()
        
    @threaded()
    def run_script_t(self, script_file):
        return self.run_script(script_file)
