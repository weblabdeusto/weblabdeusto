#!/bin/bash

celery -A wcloud.tasks.create worker -Q createtasks --loglevel=DEBUG --concurrency=1
