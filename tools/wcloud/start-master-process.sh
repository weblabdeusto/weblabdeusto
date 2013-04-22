#!/bin/bash

if [ $UID != 0 ]; then
    echo "Error: run $0 as root"
    exit -1
fi

nohup python apache_reloader.py > nohup_apache_reloader &

su - weblab -c "/home/weblab/weblab/tools/wcloud/user-processes.sh"

/etc/init.d/apache2 reload
