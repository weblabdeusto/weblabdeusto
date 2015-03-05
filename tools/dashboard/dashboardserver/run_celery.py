import sys
from checks import celery_app
from checks import archimedes
celery_app.config_from_object("config")


celery_app.worker_main(sys.argv + ["-B"])