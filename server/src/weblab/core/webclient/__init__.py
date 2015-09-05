from __future__ import print_function, unicode_literals
from functools import wraps

from flask import redirect, request, url_for

from weblab.core.exc import SessionNotFoundError
from weblab.core.wl import weblab_api

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            weblab_api.api.check_user_session()
        except SessionNotFoundError:
            return redirect(url_for('.login', next=request.url))

        return func(*args, **kwargs)
    return wrapper

def reservation_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            weblab_api.api.check_user_session()
        except SessionNotFoundError:
            # TODO
            return "Reservation identifier not found"
        return func(*args, **kwargs)
    return wrapper

import view_login
import view_labs
import view_lab
import view_i18n
import view_gwt
import view_federated

assert view_login is not None and view_labs is not None and view_lab is not None and view_i18n is not None and view_gwt is not None and view_federated is not None
