#!/bin/bash

pwd
source config.sh

# The WCLOUD dir is generally the one this script is called from.

echo -n "Starting existing instances... " | tee -a nohup_start_existing_instances
date >> nohup_start_existing_instances
nohup python wcloud/start_existing_instances.py >> nohup_start_existing_instances 2>&1 &
echo "Look at nohup_start_existing_instances"
