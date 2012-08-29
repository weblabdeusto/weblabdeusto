This directory used to contain several scripts, now deprecated by weblab-script:

 - cli: the Administration Command Line Interface (you can add users, add
   permissions, etc. from here).

   # DEPRECATED: USE "weblab-script admin weblab-instance"

 - monitor: it will connect in a low level way to the running server to retrieve
   information of the current queue, etc., as well as to kick current users

   # DEPRECATED: USE "weblab-script monitor weblab-instance"

 - web: a set of scripts that require mod_python that make it easier to retrieve
   certain information such as who used WebLab recently, etc.

   # TO-BE-DEPRECATED: A FLASK INTERFACE WILL PROVIDE THE SAME FUNCTIONALITY

 - logging: a logging file generator (it creates the loggin configuration files
   automatically), and a tool to check what calls never ended, similar to apache
   forensiclog

   # DEPRECATED: NOW THIS SCRIPT CAN BE FOUND IN /tools/logging/

