from __future__ import print_function, unicode_literals
"""
This file pretends to make it possible that all the unit tests use a particular and somehow configurable 
port range (e.g. 10500 - 11000), so as to avoid conflicts with other applications. At this moment, the 
system uses random ports which are in conflict with production systems when
tests are run (e.g. in the continuous integration server).
"""

STARTING_PORT  = 10000
RESERVED_PORTS =   500 # for static files, etc.

CURRENT_PORT = STARTING_PORT + RESERVED_PORTS

def new():
    global CURRENT_PORT
    port = CURRENT_PORT
    CURRENT_PORT += 1
    return port
