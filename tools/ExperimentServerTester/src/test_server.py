#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

import SimpleXMLRPCServer

class Server(object):

    def dispose(self):
        return "DISPOSE OK"
    
    def start_experiment(self):
        return "EXPERIMENT STARTED"

    def test_me(self, message):
        return message

    def send_command_to_device(self, cmd):
        return "Response to '%s'" % cmd
        
    def login_based_on_client_address(self, username, ip):
        print "username = %s\nip = %s" % (username, ip)
        if username == 'test' and str(ip)[0] in ('8', '1'):
            return { 'id' : '1234' }
        if username == 'fault':
            raise SimpleXMLRPCServer.Fault('XMLRPC:Error002', 'Error.')
        raise SimpleXMLRPCServer.Fault('XMLRPC:Client.Authentication', 'Err2')

    def send_file_to_device(self, file_content, file_info):
        session_id = 0
        if file_info == 'generate_error':
            raise SimpleXMLRPCServer.Fault('XMLRPC:Error001', 
                "ERROR. Session: %s; File info: %s; File size: %s" % (
                    session_id,
                    file_info,
                    len(file_content)
                ))

        return "Session: %s; File info: %s; File size: %s" % (
                    session_id,
                    file_info,
                    len(file_content)
                )
				

server = SimpleXMLRPCServer.SimpleXMLRPCServer(("",12345))
#server = SimpleXMLRPCServer.SimpleXMLRPCServer('http://127.0.0.1:12345')
server.register_instance(Server())
server.serve_forever()
