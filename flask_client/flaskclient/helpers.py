from collections import defaultdict
import re
from urlparse import urlparse, urljoin
from flask import request, url_for, redirect, json
import requests
from flaskclient.flask_app import flask_app
from flaskclient.weblabweb import WeblabWeb



def build_experiments_list(experiments_list, experiments_config):
    """
    Builds a merged experiments list which contains, for only those experiments which the user
    is allowed to use, the extra information contained within experiments_config.

    @param experiments_list {list[object]}: List of experiments, provided by the experiments_list Weblab method.
    @param experiments_config {dict}: Configuration JS file (which will eventually be removed).
    @returns {dict[object], dict[object]}: Experiments dictionary, experiments_by_category
    """
    experiments = {}
    experiments_by_category = defaultdict(list)

    # First, store the info available from the experiments_list into the experiments registry.
    for exp_data in experiments_list:
        category = exp_data["experiment"]["category"]["name"]
        exp_name = exp_data["experiment"]["name"]
        time_allowed = exp_data["time_allowed"]
        experiments["%s@%s" % (exp_name, category)] = {"time_allowed": time_allowed}

    # Now, merge the data from experiments_config into the experiments which are available for the user.
    # (experiments config contains the list of all experiments, not just those that the user should see).
    exps = experiments_config["experiments"]
    for exp_type, exp_list in exps.items():
        for exp_config in exp_list:
            key = exp_config["experiment.name"] + "@" + exp_config["experiment.category"]
            if key in experiments:
                exp_config["experiment_type"] = exp_type
                experiments[key].update(exp_config)
                experiments_by_category[exp_config["experiment.category"]].append(experiments[key])

    return experiments, experiments_by_category


def _retrieve_configuration_js():
    """
    Returns the configuration JS. This is mostly for the configuration function, but
    also so that it can be used from outside. This will eventually be removed altogether
    when the configuration.js file disappears.

    @see configuration
    @rtype str
    """
    config = requests.get(flask_app.config["LAB_URL"] + "configuration.js")
    js = config.content

    def remove_comments(string):
        """
        Removes comments from a string, supports // and /* formats. From Stack Overflow.
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

    js = remove_comments(js)

    return js




# Redirection utils from Flask manual / pocoo.
# http://flask.pocoo.org/snippets/62/

def is_safe_url(target):
    """
    Checks if an URL is safe for redirection via URL.
    # TODO: Reportedly by some comments not a safe check.
    :param target:
    :return:
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def get_redirect_target():
    """
    Find out where we need to redirect.
    :return:
    """
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target

def redirect_back(endpoint, **values):
    target = request.form['next']
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)






# Retrieves the experiments data. This is extremely inefficient, but it's just a temporary
# way of handling this until configuration.js is gone etc.
def get_experiments_data(sessionid, route):
    # To properly render the labs list we need access to the configuration.js file (this will change in the
    # future). We actually request this to ourselves.
    config = _retrieve_configuration_js()
    config = json.loads(config)

    weblabweb = WeblabWeb()
    weblabweb.set_target_urls(flask_app.config["LOGIN_URL"], flask_app.config["CORE_URL"])
    weblabweb._feed_cookies(request.cookies)
    weblabweb._feed_cookies({"weblabsessionid": "%s.%s" % (sessionid, route)})

    print "LISTING EXPERIMENTS WITH: (%s, %s)" % (sessionid, route)

    experiments_list = weblabweb._list_experiments(sessionid)
    # TODO: There could be issues with the routing.

    # Merge the data for the available experiments.
    experiments, experiments_by_category = build_experiments_list(experiments_list, config)

    return experiments, experiments_by_category