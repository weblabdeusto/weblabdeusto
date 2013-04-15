#!/bin/bash

if [ $UID != 0 ]; then
    echo "Error: run $0 as root"
    exit -1
fi

killall weblab-admin
killall python
killall redis-server
