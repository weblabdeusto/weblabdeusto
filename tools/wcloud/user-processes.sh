#!/bin/bash

export WCLOUD_REDIS=/home/weblab/redis_env

cd ${WCLOUD_REDIS}
./launch.sh

cd /home/weblab/weblab/tools/wcloud/
. /usr/local/bin/virtualenvwrapper.sh
workon weblab

export WCLOUD_SETTINGS=/home/weblab/weblab/tools/wcloud/secret_settings.py
export PYTHONPATH=.
export http_proxy=http://proxy-s-priv.deusto.es:3128/
export https_proxy=https://proxy-s-priv.deusto.es:3128/

sleep 2 # Wait until Redis servers are loaded before starting WebLab-Deusto instances

echo -n "Starting taskmanager..."
nohup python wcloud/taskmanager.py > nohup_taskmanager 2>&1 &
echo "Look at nohup_taskmanager"

echo -n "Starting weblab starter... "
nohup python wcloud/weblab_starter.py > nohup_weblab_starter 2>&1 &
echo "Look at nohup_weblabstarter"
