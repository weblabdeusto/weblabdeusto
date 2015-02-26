import os
import time

FILE = "MeasuereServer.log"
RESTART_COMMANDS = ["echo hello"]

def restart():
    print "Error code detected in the log: RESTARTING"

    for c in RESTART_COMMANDS:
        os.system(c)

    print "Restart should be over."

def main():

    print "Running..."

    file_top = os.path.getsize(FILE)

    while True:

        current_size = os.path.getsize(FILE)

        if current_size > file_top:
            # Read the changes.
            f = open(FILE)
            f.seek(file_top)
            added = f.read()

            if "Error code: -1074130544" in added:
                restart()

            file_top = current_size

        time.sleep(5)


main()