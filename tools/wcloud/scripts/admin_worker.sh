#!/bin/bash

# This script is meant to be run as root
if [ $UID != 0 ]; then
    echo "Error: run $0 as root"
    exit -1
fi

celery -A wcloud.tasks.admin_tasks worker -Q admintasks --loglevel=DEBUG --concurrency=1
