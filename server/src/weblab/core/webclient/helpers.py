from __future__ import print_function, unicode_literals
from collections import defaultdict
from functools import wraps
import hashlib
import json
import os
import re
import urllib
import urlparse

from weblab.core.wl import weblab_api
from flask import current_app

class WebError(Exception):
    pass

def json_exc(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except WebError as e:
            return weblab_api.jsonify(error=True, message=e.args[0])
        except Exception:
            if current_app.debug:
                raise
            traceback.print_exc()
            return weblab_api.jsonify(error=True, message=gettext("Error processing request"))
    return wrapped

def web_exc(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except WebError as e:
            return weblab_api.make_response(gettext(e.args[0]), 500)
        except Exception:
            if current_app.debug:
                raise
            traceback.print_exc()
            return weblab_api.make_response(gettext("Error processing request"), 500)
    return wrapped

def remove_comments_from_json(string):
    """
    Removes comments from a JSON string, supports // and /* formats. From Stack Overflow.
    @param str string: Original text.
    @return: Text without comments.
    @rtype: str
    """
    pattern = r"((?<!\\)\".*?(?<!\\)\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
    # first group captures quoted strings (double or single)
    # second group captures comments (//single-line or /* multi-line */)
    regex = re.compile(pattern, re.MULTILINE | re.DOTALL)

    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        if match.group(2) is not None:
            return ""  # so we will return empty to remove the comment
        else:  # otherwise, we will return the 1st group
            return match.group(1)  # captured quoted-string

    return regex.sub(_replacer, string)


def safe_redirect(redir):
    """
    Returns a safe version of the specified path. If the path is not relative to the application's index, then it
    return None.

    @param redir: Redirection path or similar. Can be unsafe. If it is not a valid path None is returned.
    @return: A safe redirection string, or None.
    """
    try:
        redirurl = urlparse.urlparse(redir)
        current_url = urlparse.urlparse(weblab_api.ctx.core_server_url)
        if redirurl.netloc not in (None, '', current_url.netloc):
            return None
        redir = redirurl.geturl()
        return redir
    except Exception:
        return None


def _get_gravatar_url():
    """
    Returns the gravatar URL 
    :return: gravatar URL
    :rtype: unicode
    """
    # TODO: default to the /avatar/ thing; change the db to support that 
    # /weblab/web/avatars/<hidden-id>.jpg is that URL if the user doesn't 
    # have any gravatar URL

    # Retrieve user information
    if weblab_api.current_user:
        email = weblab_api.current_user.email

        # Calculate the Gravatar from the mail
        gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'d': "http://placehold.it/150x150", 's': str(50)})
        return gravatar_url
    return None

def _get_experiment(experiment_raw):
    """
    Retrieves a simple dictionary with the most important data of the experiment object.
    :rtype: dict
    """
    exp = {}
    exp["name"] = experiment_raw.experiment.name
    exp["category"] = experiment_raw.experiment.category.name
    exp["time"] = experiment_raw.time_allowed
    exp["type"] = experiment_raw.experiment.client.client_id
    exp["config"] = experiment_raw.experiment.client.configuration
    return exp

