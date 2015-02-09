from celery import Celery

celery_app = Celery("celery_tasks", broker="redis://localhost:6379", backend="redis://localhost:6379")

celery_app.conf.update(
    CELERY_ROUTES = {
        'wcloud.tasks.admin_tasks.apache_reload': {'queue': 'admintasks'},
        'wcloud.tasks.starter_tasks.start_weblab': {'queue': 'startertasks'},
        'wcloud.tasks.starter_tasks.start_redis': {'queue': 'startertasks'},
        'wcloud.tasks.create.deploy_weblab_instance': {'queue': 'createtasks'},
    },
    CELERY_TASK_SERIALIZER = 'json',
    CELERY_ACCEPT_CONTENT=('json',),
    CELERY_RESULT_SERIALIZER = 'json',
)
