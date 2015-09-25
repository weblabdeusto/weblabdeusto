# Runs the labserver-side bridge.
import sys

from common import cfg
import signal
from exp_bridge.comms.exps.ExpConnector import ExpConnector

config = cfg.parse_config("config.yml")
cfg.verify_config(config)

# ExpConnector registry. Each one will keep a connection to one local Experiment Server.
exp_connectors = []
""" :type : [ ExpConnector ] """

# Register all the ExpConnectors defined in the configuration. The Exp Connectors will automatically
# try to connect to the right Experiment Server.
for exp_name, exp in config["exp_bridge"]["experiments"].items():
    port = exp["port"]
    host = exp.get("host", "127.0.0.1")
    path = exp.get("path", "/")  # TODO: Set a proper default.
    exp_connector = ExpConnector(exp_name, host, port, path) # TODO: path support
    print("Registered Exp Connector for {0} on {1}:{2}".format(exp_name, host, port))
    greenlet = exp_connector.start()
    exp_connectors.append(exp_connector)



# Be ready to quit if needed.
def signal_handler(signal, frame):
    print "CTRL+C detected. Turning off."
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print("Running. Press CTRL+C to exit.")
signal.pause()






