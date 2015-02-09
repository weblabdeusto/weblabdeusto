#!/bin/bash

pwd
source config.sh

# The WCLOUD dir is generally the one this script is called from.

sleep 2 # Wait until Redis servers are loaded before starting WebLab-Deusto instances

echo -n "Starting taskmanager..." | tee -a nohup_create
date >> nohup_create
nohup scripts/create_worker.sh >> nohup_create 2>&1 &
echo "Look at nohup_taskmanager"

echo -n "Starting starter..." | tee -a nohup_starter
date >> nohup_starter
nohup scripts/starter_worker.sh >> nohup_starter 2>&1 &
echo "Look at nohup_starter"

echo -n "Starting weblab starter... " | tee -a nohup_weblab_starter
date >> nohup_weblab_starter
nohup python wcloud/weblab_starter.py >> nohup_weblab_starter 2>&1 &
echo "Look at nohup_weblabstarter"
