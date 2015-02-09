import os
import time
import subprocess

from wcloud import app as flask_app
from wcloud.tasks.celery_app import celery_app

@celery_app.task(bind=True, name='start_weblab')
def start_weblab(self, dirname, wait):
    stdout_path = os.path.join(dirname, "stdout.txt")
    stderr_path = os.path.join(dirname, "stderr.txt")

    print "Starting instance: %s" % dirname,

    process = subprocess.Popen(['nohup','weblab-admin', 'start', dirname],
                stdout = open(stdout_path, 'w+', 0),
                stderr = open(stderr_path, 'w+', 0),
                stdin  = subprocess.PIPE)

    print "[done]"

    if wait:
        wait_process(process)

    errors = open(stderr_path).read()
    print "[dbg] Stderr: " + errors
    print "[dbg:END OF STDERR]"

    logs = open(stdout_path).read()
    print "[dbg] Stdout: " + errors
    print "[dbg:END OF STDOUT]"
    return

def wait_process(process):
    """
    Checks that the Process is running for the number of seconds specified in the configuration.
    If within that time the process stops running, an exception is thrown.
    """

    print "Waiting for process to start and stay..."

    time_to_wait = flask_app.config.get("WEBLAB_STARTUP_TIME", 20)

    start_time = time.time()

    # Wait for some seconds to start with. Apparently POPEN() did not immediately start the process in some instances.
    # This meant than when we ran the following check, it was mistakenly reported as a failure.
    # TODO: The 4 here is a magic number. This should probably be improved. Ideally, with a better way to detect
    # failures.
    time.sleep(7)
    if time_to_wait > 7:
        time_to_wait -= 7

    while time.time() - start_time < time_to_wait:
        if process.poll() is not None:  # Ensure that the process does not finish early.
            raise Exception("Weblab was apparently not started successfully (not running after %f seconds)" % (time.time() - start_time))

    # TODO: we should check whether the process is started (e.g., contacting the port periodically)

def stop_weblab(dirname):
    print "Stopping instance: %s" % dirname,
    try:
        result = subprocess.check_output(['weblab-admin', 'stop', dirname])
    except subprocess.CalledProcessError:
        return False

    print "[done]"
    return True


@celery_app.task(bind=True, name='start_redis')
def start_redis(self, directory, config_file, port):
    stdout_path = os.path.join(directory, "stdout_redis_%s.txt" % port)
    stderr_path = os.path.join(directory, "stderr_redis_%s.txt" % port)

    subprocess.Popen(['nohup','redis-server', directory, config_file],
                stdout = open(stdout_path, 'w+', 0),
                stderr = open(stderr_path, 'w+', 0),
                stdin  = subprocess.PIPE)

