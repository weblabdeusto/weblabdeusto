from wcloud.tasks.celery_app import celery_app

@celery_app.task(bind=True, name='apache_reload')
def apache_reload(self):
    return ":-)"
