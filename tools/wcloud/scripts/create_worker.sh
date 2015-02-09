#!/bin/bash

celery -A wcloud.tasks.create worker -Q createtasks --loglevel=info
