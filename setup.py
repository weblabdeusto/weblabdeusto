#!/usr/bin/env python
import subprocess
import os
import sys

cwd = os.path.abspath(os.getcwd())
os.chdir(os.path.join('server','src'))
try:    
    new_argv = [sys.executable]
    new_argv.extend(sys.argv)
    subprocess.call(new_argv, shell = False)
finally:
    os.chdir(cwd)
