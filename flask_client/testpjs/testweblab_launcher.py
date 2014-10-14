import os
import threading
import sys
import time

original_path = os.path.abspath(os.curdir)

weblab_path = "../../server/launch/sample"
os.chdir(weblab_path)
sys.path.append(".")

from launch_sample import inner

condition = threading.Condition()
event_notifier = threading.Condition()


class Runner(threading.Thread):
    def run(self):
        self.launcher = inner(condition=condition, event_notifier=event_notifier)
        self.launcher.launch()


runner = Runner()
runner.start()

with event_notifier:
    event_notifier.wait()

os.chdir(original_path)

result = os.system(
    "mocha-phantomjs -s web-security=no -s localToRemoteUrlAccessEnabled=true -s webSecurityEnabled=false testrunner.html")

os.chdir(weblab_path)

if sys.argv[1] == "forever":
    sys.exit(result)

if sys.argv[2] == "wait":
    time.sleep(int(sys.argv[3]))

with condition:
    condition.notify()

sys.exit(result)
