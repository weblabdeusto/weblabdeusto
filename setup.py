#!/usr/bin/env python
import os
import sys

cwd = os.path.abspath(os.getcwd())
os.chdir(os.path.join('server','src'))
try:    
    sys.path.insert(0, os.getcwd())
    execfile("setup.py")
finally:
    os.chdir(cwd)
