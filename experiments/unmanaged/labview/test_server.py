HOST = 'localhost'
PORT = 20000
# PORT = 80
WEBLAB_SECRET = "12345@&"
DEBUG_MESSAGE = True
DEBUG_COMMAND = True

import socket
import time

def _dbg_message(msg): 
    if DEBUG_MESSAGE: 
        print msg

def _dbg_command(msg): 
    if DEBUG_COMMAND: 
        print msg

def _send_message(message):
    message = message + '\r\n'
    _dbg_message("Creating socket")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _dbg_message("Connecting...")
    s.connect((HOST, PORT))
    _dbg_message("Connected. Sending message: %s" % message)
    s.send(message)
    _dbg_message("Message sent")
    _dbg_message("Waiting for response")
    response = s.recv(1024)
    _dbg_message("Response received: %r" % response)
    _dbg_message("Closing socket")
    s.close()
    _dbg_message("Socket closed")
    return response
    
def start(client_key, username, url, time):
    message = '@@@'.join(('start', WEBLAB_SECRET, client_key, username, url, str(time)))
    _send_message(message)

def status(client_key):  
    message = '@@@'.join(('status', WEBLAB_SECRET, client_key))
    response = _send_message(message)
    if response:
        try:
            status_result = int(response.strip())
        except:
            pass

def end(client_key):
    message = '@@@'.join(('end', WEBLAB_SECRET, client_key))
    _send_message(message)


# Use example
_dbg_command("Starting for unai...")
start('CLIENT_KEY', 'unai', 'https://weblab.deusto.es/weblab/client/?locale=es#page=experiment&exp.category=PLD%20experiments&exp.name=ud-test-pld2', 192)
_dbg_command("Started")

time.sleep(2)

_dbg_command("Current status...")
status_result = status('CLIENT_KEY')
_dbg_command("status: %r" % status_result)

time.sleep(2)
_dbg_command("end")
end('CLIENT_KEY')
_dbg_command("ended")

print "Now fast in a loop"

USER = 'unai'

for x in range(10):
    if USER == 'unai':
        USER = 'pablo'
    else:
        USER = 'unai'

    _dbg_command("Starting for %s..." % USER)
    start('CLIENT_KEY', USER, 'https://weblab.deusto.es/weblab/client/?locale=es#page=experiment&exp.category=PLD%20experiments&exp.name=ud-test-pld2', 192)
    _dbg_command("Started")
    _dbg_command("Current status...")
    status_result = status()
    _dbg_command("status: %r" % status_result)
    _dbg_command("end")
    end()
    _dbg_command("ended")

