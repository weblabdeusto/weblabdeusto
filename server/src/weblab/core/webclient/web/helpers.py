from collections import defaultdict
import hashlib
import json
import os
import re
import urllib
import urlparse
from flask import url_for
from weblab.core.wl import weblab_api


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
        if redirurl.netloc not in (None, ''):
            return None
        redir = redirurl.geturl()
        return redir
    except Exception as ex:
        return None



# # Redirection utils from Flask manual / pocoo.
# # http://flask.pocoo.org/snippets/62/
#
# def is_safe_url(target):
#     """
#     Checks if an URL is safe for redirection via URL.
#     # TODO: Reportedly by some comments not a safe check.
#     :param target:
#     :return:
#     """
#     ref_url = urlparse(request.host_url)
#     test_url = urlparse(urljoin(request.host_url, target))
#     return test_url.scheme in ('http', 'https') and \
#            ref_url.netloc == test_url.netloc
#
#
# def get_redirect_target():
#     """
#     Find out where we need to redirect.
#     :return:
#     """
#     for target in request.values.get('next'), request.referrer:
#         if not target:
#             continue
#         if is_safe_url(target):
#             return target
#
# def redirect_back(endpoint, **values):
#     target = request.form['next']
#     if not target or not is_safe_url(target):
#         target = url_for(endpoint, **values)
#     return redirect(target)
#
#
#
#
#
#


def _get_loggedin_info():
    """
    Returns a dictionary with several parameters to render the logged_in part of the website.
    PRERREQUISITE: weblab_api.ctx.reservation_id must be set.
    :return: info dictionary
    :rtype: dict
    """

    # Retrieve the configuration.js info.
    deployment_dir = weblab_api.config.get("deployment_dir")
    configuration_js_path = os.path.join(*[deployment_dir, "configuration.js"])
    configuration_js = open(configuration_js_path).read()
    configuration_js = remove_comments_from_json(configuration_js)
    configuration_js = json.loads(configuration_js)

    # Retrieve user information
    user_info = weblab_api.api.get_user_information()

    # Calculate the Gravatar from the mail
    gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(user_info.email.lower()).hexdigest() + "?"
    gravatar_url += urllib.urlencode({'d': "http://placehold.it/150x150", 's': str(50)})

    info = {}
    core_server_url = weblab_api.server_instance.core_server_url
    info["logo_url"] = os.path.join(*[core_server_url, "client", "weblabclientlab", configuration_js["host.entity.image"].lstrip('/')])
    info["host_link"] = configuration_js["host.entity.link"]
    info["full_name"] = user_info.full_name
    info["gravatar"] = gravatar_url

    return info


def _get_experiment_info(experiments_raw):
    """
    Retrieves a data-only dict with the allowed experiments by name and an index of these same experiments
    by their categories.
    :param experiments_raw: Raw experiments list as returned by list_experiments API.
    :return: (experiments, experiments_by_category)
    """
    experiments = {}
    experiments_by_category = defaultdict(list)

    for raw_exp in experiments_raw:
        exp = {}
        exp["name"] = raw_exp.experiment.name
        exp["category"] = raw_exp.experiment.category.name
        exp["time"] = raw_exp.time_allowed
        exp["type"] = raw_exp.experiment.client.client_id
        exp["config"] = raw_exp.experiment.client.configuration

        experiments[exp["name"]] = exp
        experiments_by_category[exp["category"]].append(exp)

    return experiments, experiments_by_category