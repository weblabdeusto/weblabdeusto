#!/bin/bash

celery -A wcloud.tasks.admin_tasks worker -Q admintasks --loglevel=info
