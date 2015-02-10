
from flaskapp import app
from tasks import starter_tasks
import glob
import os
import re

import wcloud.tasks.starter_tasks


# Issue a task for each existing weblab instance
print "Creating tasks for starting existing weblab instances..."
instances_dir_base = app.config["DIR_BASE"]

instance_dirs = glob.glob(os.path.join(instances_dir_base, "*"))
for instance_dir in instance_dirs:
    starter_tasks.start_weblab.delay(instance_dir, 20)

# Issue a task for each existing redis configuration file
print "Creating tasks for starting existing redis instances..."
redis_folder = app.config["REDIS_FOLDER"]
redis_instances = glob.glob(os.path.join(redis_folder, "/*.conf"))

for redis_instance in redis_instances:
    # Find out the alleged port for the instance. This can be obtained from the name, but the 'real'
    # definition is in the config file itself. Maybe the start_redis method should actually be
    # changed so as not to require the port. TODO:
    filename = os.path.basename(redis_instance)
    directory = os.path.dirname(redis_instance)
    m = re.match(""".*_([0-9]+)\.conf""", filename)
    try:
        port = m.group(1)
    except:
        # TODO: Consider whether we should avoid throwing an exception here so that the supposedly correct instances
        # can actually start.
        raise Exception("ERROR starting redis instances. Could not start them due to wrong conf file: %s" % redis_instance)
    starter_tasks.start_redis(directory, filename, port)