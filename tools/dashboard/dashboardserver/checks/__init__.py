

from celery import Celery

celery_app = Celery('tasks', broker='redis://', backend='redis://')

@celery_app.task
def check_http_get_code(check_id, url, code):
    """
    Checks that the specified url responds with the specified HTTP code.
    :param check_id: ID of the check.
    :param url: URL to do the HTTP GET against.
    :param code: Expected code.
    :return:
    """
    pass

@celery_app.task
def check_http_get_response(check_id, url, regex):
    """
    Checks that the content that the specified URL returns contains the specified regex.
    :param check_id: ID of the chck.
    :param url: URL to do the HTTP GET against.
    :param regex: Regex to check the response with.
    :return:
    """
    pass