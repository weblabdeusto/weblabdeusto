#!/bin/bash

# When running the worker, we don't attend pending requests: we first remove them
# celery -A wcloud.tasks.starter_tasks redis queue.purge startertasks
celery -A wcloud.tasks.starter_tasks worker -Q startertasks --loglevel=DEBUG --concurrency=1
