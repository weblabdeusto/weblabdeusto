#!/usr/bin/env python
import os
import sys
import shutil

"""
WebLab-Deusto setup script. Running:

   python setup.py install 
   
will install the whole WebLab-Deusto system (a virtualenv is recommended).

The pure Python project is stored in server/src. In client you may find a 
pure Java project for the client (developed with Google Web Toolkit). We 
keep this setup.py here (which actually calls the server/src/setup.py
script) so as to support:

   pip install git+https://github.com/weblabdeusto/weblabdeusto.git

However, some dirty things are required for this (given that this project
does not follow the Python convention of using the root project directly),
such as moving the pip-egg-info directory, etc.
"""

# 
# XXX: Kludge: pip creates a pip-egg-info directory where it stores information.
# If it has been created, we move it to the server/src directory, and then return
# it at the end of the script.
# 

if os.path.exists('pip-egg-info') and not os.path.exists(os.path.join('server','src','pip-egg-info')):
    shutil.move('pip-egg-info', os.path.join('server','src'))
    must_move_egg_info = True
else:
    must_move_egg_info = False


# 
# Here is the real work. We use execfile instead of subprocess.call so as to
# avoid duplicating the process (some errors have been generated in the past
# due to this).
# 
cwd = os.path.abspath(os.getcwd())
os.chdir(os.path.join('server','src'))
try:    
    sys.path.insert(0, os.getcwd())
    execfile("setup.py")
finally:
    os.chdir(cwd)

    #
    # Move the pip-egg-info back, if required
    # 

    if must_move_egg_info:
        shutil.move(os.path.join('server','src','pip-egg-info'), os.getcwd())

