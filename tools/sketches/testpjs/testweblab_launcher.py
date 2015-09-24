from __future__ import print_function, unicode_literals
"""
Launches a local Weblab instance which makes use of the launch_sample configuration, and runs
on it the WeblabWeb tests using PhantomJS. Once the tests are run, the instance is automatically
stopped.
"""


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


with condition:
    condition.notify()

sys.exit(result)
