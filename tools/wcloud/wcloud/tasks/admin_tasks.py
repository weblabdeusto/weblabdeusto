from wcloud.tasks.celery_app import celery_app

import subprocess


class ApacheReloadException(Exception):
    pass


@celery_app.task(bind=True)
def apache_reload(self):
    result = subprocess.check_call(["/etc/init.d/apache2", "reload"])

    if result != 0:
        # Something happened.
        raise ApacheReloadException()

    return

