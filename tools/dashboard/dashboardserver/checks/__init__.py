import datetime
import requests
import redis
from celery import Celery

celery_app = Celery('tasks', broker='redis://', backend='redis://')

r = redis.StrictRedis(host='localhost', db=0)


def enum(**enums):
    return type('Enum', (), enums)

TASK_STATE = enum(
    UNKNOWN='unknown',
    RUNNING='running',
    FINISHED='finished'
)


def report(task_state, check_id, msg, result):
    """
    Reports a check result.
    :param task_state: State of the task.
    :param check_id: ID of the check.
    :param msg: Message to display (will generally be the same despite the result)
    :param result: Result.
    :return:
    """
    if task_state == TASK_STATE.RUNNING:
        r.set("dashboard:checks:%s:msg" % (check_id), msg)
        r.set("dashboard:checks:%s:task_state" % (check_id), task_state)
    elif task_state == TASK_STATE.FINISHED:
        r.set("dashboard:checks:%s:task_state" % (check_id), task_state)
        r.set("dashboard:checks:%s:result" % (check_id), result)
        r.set("dashboard:checks:%s:finished_date" % (check_id), datetime.datetime.utcnow())

def read_check(check_id):
    """
    Reads the state of a check.
    :param check_id: ID of the check.
    :return:
    """
    check = {}
    for var in ("task_state", "msg", "result", "finished_date"):
        check[var] = r.get("dashboard:checks:%s:%s" % (check_id, var))
    return check


@celery_app.task(name="check.http_get_code")
def check_http_get_code(check_id, msg, url, code):
    """
    Checks that the specified url responds with the specified HTTP code.
    :param check_id: ID of the check.
    :param msg: Msg to display.
    :param url: URL to do the HTTP GET against.
    :param code: Expected code.
    :return:
    """
    result = None
    report(TASK_STATE.RUNNING, check_id, msg, result)

    try:
        req = requests.get(url)
        stcode = req.status_code
        if stcode != code:
            result = "ERROR"
        else:
            result = "OK"
    except:
        result = "FAIL"

    report(TASK_STATE.FINISHED, check_id, msg, result)

@celery_app.task(name="check.http_get_response")
def check_http_get_response(check_id, msg, url, regex):
    """
    Checks that the content that the specified URL returns contains the specified regex.
    :param check_id: ID of the chck.
    :param msg: Msg to display.
    :param url: URL to do the HTTP GET against.
    :param regex: Regex to check the response with.
    :return:
    """
    return "OK"