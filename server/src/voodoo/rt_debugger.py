#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009 University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
#
"""
This code has been adapted from the simplebtconsole.py of Nokia Python for S60.

It shouldn't be used but for debugging purposes in debugging environments. Calling "launch_debugger()" will
launch a single-thread socket server which will provide, *with no password* a Python console to the client.
From this Python console, the user will be able to interact with any structure running at the time.

"""

import sys
import socket
import code
import threading

import voodoo.counter as counter

class RtDebugger(object):
    def __init__(self,sock,realio):
        self.socket = sock
        self.stdout, self.stdin, self.stderr = realio
        self.latest   = ''
    def read(self,n=1):
        return self.socket.recv(n).replace('\r\n','\n')
    def write(self,str):
        return self.socket.send(str.replace('\n','\r\n'))
    def readline(self,n=None):
        buffer=[]
        while 1:
            ch=self.read(1)
            if len(ch) == 0:
                break
            if ch == '\n' or ch == '\r':
                if self.latest == '\r': # If a \r\n is sent, just ignore it
                    self.latest = ''
                    continue
                buffer.append('\n')
                break
            if ch == '\177' or ch == '\010':
                del buffer[-1:]
            else:
                buffer.append(ch)
            if n and len(buffer)>=n:
                break
        self.latest = ch
        return ''.join(buffer)
    def raw_input(self,prompt=""):
        self.write(prompt)
        return self.readline()
    def flush(self):
        pass

class Debugger(threading.Thread):
    def __init__(self, banner, port):
        threading.Thread.__init__(self)
        self.setName(counter.next_name("Debugger"))
        self.banner = banner
        self.port   = port
    def run(self):
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.bind(('localhost',self.port))
        except:
            # If I can't bind, there is nothing I cand do
            return
        self.sock.listen(5)

        while True:
            s, address = self.sock.accept()
            print "Conection from %s" % str(address)

            realio = sys.stdout, sys.stdin, sys.stderr
            socketio = RtDebugger(s, realio)
            sys.stdout,sys.stdin,sys.stderr = socketio,socketio,socketio

            try:
                try:
                    code.interact(banner=self.banner)
                finally:
                    sys.stdout, sys.stdin, sys.stderr = realio
            except Exception as e:
                print e
            except SystemExit as e:
                print e

            try:
                s.close()
            except:
                pass

    def close(self):
        self.sock.close()

_dbg = None
_dbg_lock = threading.Lock()

def launch_debugger(port = 31337):
    banner = "Welcome to WebLab.\nFrom this interactive shell you can access the internal structures directly.\n%s" % sys.version
    # Launch only one
    global _dbg_lock
    global _dbg
    _dbg_lock.acquire()
    try:
        if _dbg is None:
            _dbg = Debugger(banner, port)
            _dbg.setDaemon(True)
            _dbg.start()
    finally:
        _dbg_lock.release()

def stop_debugger():
    if _dbg is not None:
        try:
            _dbg.close()
        except Exception as e:
            print e

