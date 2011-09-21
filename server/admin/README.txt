This directory contains administration scripts:

 - cli: the Administration Command Line Interface (you can add users, add
   permissions, etc. from here)

 - monitor: it will connect in a low level way to the running server to retrieve
   information of the current queue, etc., as well as to kick current users

 - web: a set of scripts that require mod_python that make it easier to retrieve
   certain information such as who used WebLab recently, etc.

 - logging: a logging file generator (it creates the loggin configuration files
   automatically), and a tool to check what calls never ended, similar to apache
   forensiclog

