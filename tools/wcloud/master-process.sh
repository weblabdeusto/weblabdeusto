#!/bin/bash
nohup python apache_reloader.py > nohup_apache_reloader &

su - weblab -c "/home/weblab/weblab/tools/wcloud/user-processes.sh"
