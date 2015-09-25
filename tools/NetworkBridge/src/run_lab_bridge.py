# Runs the labserver-side bridge.
import sys

from common import cfg
import signal
from lab_bridge.comms.expbridge.LongPollingConnector import LongPollingConnector
from lab_bridge.comms.lab.LabListener import LabListener

config = cfg.parse_config("config.yml")
cfg.verify_config(config)

# LabListener registry. Each one can listen for several experiments.
lab_listeners = []
""" :type : [ lablistener.LabListener ] """

# Register all the LabListeners defined in the configuration. The LabListeners pretend to be
# ExperimentServers (from the perspective of the Laboratory Server).
for exp_name, exp in config["lab_bridge"]["experiments"].items():
    port = exp["port"]
    host = exp.get("host", "127.0.0.1")
    path = exp["path"]
    listener = LabListener(exp_name, host, port, path)  # TODO: path support
    print("Registered listener on {0}:{1}".format(host, port))
    greenlet = listener.start()
    lab_listeners.append(listener)

# ExpBridge connectors. Those are also listeners and they act as bridges.
exp_bridge_connectors = []
""" :type : [ BaseConnector ] """

# Listen for ExpNetworkWrapper connections
for bridge_name, bridge in config["lab_bridge"]["exp_bridges"].items():
    proto = bridge["proto"]
    type = proto["type"]
    host = proto["host"]
    port = proto["port"]
    connector = LongPollingConnector(host, port)
    greenlet = connector.start()
    exp_bridge_connectors.append(connector)


# Be ready to quit if needed.
def signal_handler(signal, frame):
    print "CTRL+C detected. Turning off."
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print("Running. Press CTRL+C to exit.")
signal.pause()






