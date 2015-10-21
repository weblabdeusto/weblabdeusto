# #!/usr/bin/python
# # -*- coding: utf-8 -*-
# #
# # Copyright (C) 2005 onwards University of Deusto
# # All rights reserved.
# #
# # This software is licensed as described in the file COPYING, which
# # you should have received as part of this distribution.
# #
# # This software consists of contributions made by many individuals,
# # listed below:
# #
# # Author: Pablo Orduña <pablo@ordunya.com>
# #         Jaime Irurzun <jaime.irurzun@gmail.com>
# #
# from __future__ import print_function, unicode_literals
#
# if __name__ == '__main__':
#     import sys
#     import time
#     f = open(sys.argv[2]).read()
#     print(f)
#     try:
#         if f.find("-file "):
#             filesent = f.split('-file')[1].strip().split('\n')[0].split(' ')[0].strip()
#             filecontent = open(filesent).read()
#             if filecontent.find("time=") >= 0:
#                 print("Sleeping")
#                 t = int(filecontent.split('time=')[1].strip().split(' ')[0].split('\n')[0].strip())
#                 time.sleep(t)
#                 print("Slept",t)
#     except:
#         pass
#     if f.find("error.file") >= 0:
#         print("ERROR: bla bla bla")
#     elif f.find("stderr.file") >= 0:
#         sys.stderr.write("bla bla bla")
#     elif f.find("return-1.file") >= 0:
#         sys.exit(-1)
