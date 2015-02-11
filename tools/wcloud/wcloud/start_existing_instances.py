import os
import sys
import re
import glob
import time
import threading

sys.path.append('.')
from wcloud import app
import wcloud.tasks.starter_tasks as starter_tasks

if __name__ == '__main__':

    # IMPORTANT: REDIS GOES FIRST (otherwise weblab will not start)

    # Issue a task for each existing redis configuration file
    print "Creating tasks for starting existing redis instances..."
    redis_folder = app.config["REDIS_FOLDER"]
    redis_instances = glob.glob(os.path.join(redis_folder, "*.conf"))

    threads = []

    for redis_instance in redis_instances:
        time.sleep(0.5)
        filename = os.path.basename(redis_instance)
        directory = os.path.dirname(redis_instance)
        print "Starting %s" % (os.path.join(directory, filename))
        t = threading.Thread(target = starter_tasks.start_redis, args = (directory, filename))
        t.start()
        threads.append(t)

    time.sleep(10)
    for t in threads:
        t.join()
    print "All redis servers started"

    # Issue a task for each existing weblab instance
    print "Creating tasks for starting existing weblab instances..."
    instances_dir_base = app.config["DIR_BASE"]
    threads = []

    instance_dirs = [ d for d in glob.glob(os.path.join(instances_dir_base, "*")) if os.path.isdir(d) ]
    for instance_dir in instance_dirs:
        t = threading.Thread(target = starter_tasks.start_weblab, args = (instance_dir, 50))
        t.start()
        threads.append(t)

    time.sleep(3)
    for t in threads:
        t.join()
    print "All WebLab-Deusto servers started"

