# Runs the labserver-side bridge.
import sys

from lab_bridge import cfg
from lab_bridge import lablistener
import signal


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
    path = exp["path", "test"]
    listener = lablistener.LabListener(host, port)  # TODO: path support
    print("Registered listener on {0}:{1}".format(host, port))
    greenlet = listener.start()
    lab_listeners.append(listener)


# Listen for ExpNetworkWrapper connections
# TODO

# Be ready to quit if needed.
def signal_handler(signal, frame):
    print "CTRL+C detected. Turning off."
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print("Running. Press CTRL+C to exit.")
signal.pause()






