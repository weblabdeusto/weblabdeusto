#!/bin/bash
cd /home/weblab/weblab/tools/wcloud/
. /usr/local/bin/virtualenvwrapper.sh
workon weblab

export WCLOUD_SETTINGS=/home/weblab/weblab/tools/wcloud/secret_settings.py
export PYTHONPATH=.
export http_proxy=http://proxy-s-priv.deusto.es:3128/
export https_proxy=https://proxy-s-priv.deusto.es:3128/
nohup python wcloud/taskmanager.py > nohup_taskmanager &
nohup python wcloud/weblab_starter.py > nohup_weblab_starter &
