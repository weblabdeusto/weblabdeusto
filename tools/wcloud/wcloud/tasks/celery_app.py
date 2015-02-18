from celery import Celery

celery_app = Celery("celery_tasks", broker="redis://localhost:6379/0", backend='redis')

celery_app.conf.update(
    CELERY_ROUTES = {
        # admin tasks (executed as root)
        'apache_reload': {'queue': 'admintasks'},
        # creation tasks (these call the starter tasks)
        'deploy_weblab_instance': {'queue': 'createtasks'},
        # starter tasks (these are called by create)
        'start_weblab': {'queue': 'startertasks'},
        'start_redis': {'queue': 'startertasks'},
    },
    CELERY_TASK_SERIALIZER = 'json',
    CELERY_ACCEPT_CONTENT=('json',),
    CELERY_RESULT_SERIALIZER = 'json',
)

