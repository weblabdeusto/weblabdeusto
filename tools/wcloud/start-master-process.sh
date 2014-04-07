#!/bin/bash

source config.sh

if [ $UID != 0 ]; then
    echo "Error: run $0 as root"
    exit -1
fi

nohup python apache_reloader.py > nohup_apache_reloader &

su $USER_ACCOUNT -c "cd $(pwd) && ./user-processes.sh"

/etc/init.d/apache2 reload
