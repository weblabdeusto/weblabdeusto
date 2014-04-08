#!/usr/bin/python

import glob
import os

config_files = glob.glob("*.conf")

for f in config_files:
    os.system("nohup redis-server %s > nohup.out 2>&1 &" % f)