# SERVERS is used by the WebLab Monitor to gather information from these ports.
# If you open them, you'll see a Python shell.
SERVERS = [
    ('127.0.0.1','10013'),
]

BASE_URL = ''

# PORTS is used by the WebLab Bot to know what
# ports it should wait prior to start using
# the simulated clients.
PORTS = {
    'soap' : [10004], 
    'soap_login' : [10000], 
    'xmlrpc' : [10005], 
    'xmlrpc_login' : [10001], 
    'json' : [10006], 
    'json_login' : [10002], 
}
