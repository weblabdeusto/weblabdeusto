#-*-*- encoding: utf-8 -*-*-

import xmlrpclib


print "Trying to establish connection (port 12345)... "
server = xmlrpclib.Server("http://localhost:12345")
print "done."

print "Sending commands... "

#test_me
#dispose

print server.test_me("Hello world")
print server.start_experiment()
print server.send_command_to_device("Command")
print server.send_file_to_device("File Contents", "File Info")
print server.dispose()

print "done."

str = raw_input()