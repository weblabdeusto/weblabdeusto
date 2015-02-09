#!/bin/bash

celery -A wcloud.tasks.wcloud_tasks worker -Q taskmanagertasks --loglevel=info
