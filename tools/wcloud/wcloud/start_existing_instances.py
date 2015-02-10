
from flaskapp import app
from tasks import starter_tasks
import glob
import os
import re

import wcloud.tasks.starter_tasks


# Issue a task for each existing weblab instance
print "Creating tasks for starting existing weblab instances..."
instances_dir_base = app.config["DIR_BASE"]

instance_dirs = [ d for d in glob.glob(os.path.join(instances_dir_base, "*")) if os.path.isdir(d) ]
for instance_dir in instance_dirs:
    starter_tasks.start_weblab.delay(instance_dir, 20)

# Issue a task for each existing redis configuration file
print "Creating tasks for starting existing redis instances..."
redis_folder = app.config["REDIS_FOLDER"]
redis_instances = glob.glob(os.path.join(redis_folder, "*.conf"))

for redis_instance in redis_instances:
    filename = os.path.basename(redis_instance)
    directory = os.path.dirname(redis_instance)
    starter_tasks.start_redis(directory, filename)
