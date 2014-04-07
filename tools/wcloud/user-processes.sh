#!/bin/bash

pwd
source config.sh

export WCLOUD_REDIS=/home/weblab/redis_env

# The WCLOUD dir is generally the one this script is called from.
WCLOUD_DIR=$(pwd)

# This is done in production but I temporarily disable it for testing.
#cd ${WCLOUD_REDIS}
#./launch.sh

cd $WCLOUD_DIR
#. /usr/local/bin/virtualenvwrapper.sh
#. workon $VIRTUALENV_NAME

. $VIRTUALENV_ACTIVATE



sleep 2 # Wait until Redis servers are loaded before starting WebLab-Deusto instances

echo -n "Starting taskmanager..."
nohup python wcloud/taskmanager.py > nohup_taskmanager 2>&1 &
echo "Look at nohup_taskmanager"

echo -n "Starting weblab starter... "
nohup python wcloud/weblab_starter.py > nohup_weblab_starter 2>&1 &
echo "Look at nohup_weblabstarter"
