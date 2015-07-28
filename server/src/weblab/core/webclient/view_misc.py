from __future__ import print_function, unicode_literals
from flask import render_template, Response

from weblab.webclient.helpers import _retrieve_configuration_js
from weblab.core.wl import weblab_api


@weblab_api.route_webclient("/contact.html")
def contact():
    return render_template("contact.html")


@weblab_api.route_webclient("/test.html")
def test():
    return render_template("test.html")


@weblab_api.route_webclient("/configuration")
def configuration():
    """
    Returns the Weblab configuration JSON file. This is mostly for testing. It will eventually
    be removed. It will also filter comments so that the contents can be parsed as valid JSON.
    @return: Configuration file as a JSON response.
    @rtype: Response
    """
    js = _retrieve_configuration_js()
    return Response(js, mimetype="application/json")


# @weblab_api.route_webclient("/redir/login/json", methods=["POST"])
# def redir_login_json():
#     """
#     Redirects a JSON post request to the Weblab login server.
#     This would normally not be necessary, but for now it is because
#     of different servers & cookie / routing issues.
#     Basically, all requests need to carry the proper weblabsesisonid cookie.
#     (Even though the request themselves carry the session too - but not the route).
#     """
#     login_url = flask_app.config.get("LOGIN_URL")
#     if login_url is None:
#         return "LOGIN URL WAS NOT SPECIFIED IN THE SERVER CONFIGURATION", 500
#
#     js = request.json
#     r = requests.post(login_url, data=json.dumps(js),
#                       headers={"Content-type": "application/json", "Accept": "text/plain"}, cookies=request.cookies)
#     """ @type: requests.Response """
#
#     response = Response(response=json.dumps(r.json()), status=r.status_code, mimetype="application/json", content_type="json")
#
#     # These cookies *may* be necessary due to the routing scheme used by Weblab.
#     # TODO: Remove this, if the routing scheme is ever changed.
#     response.set_cookie("weblabsessionid", r.cookies["weblabsessionid"])
#     response.set_cookie("loginweblabsessionid", r.cookies["weblabsessionid"])
#     response.set_cookie("route", r.cookies["weblabsessionid"].split(".")[1])
#     response.set_cookie("sessionid", r.cookies["weblabsessionid"].split(".")[0])
#
#     logging.debug("REDIR_LOGIN_JSON carried out with cookies: %r" % r.cookies)
#
#     return response
#
#
# @weblab_api.route_webclient("/redir/json", methods=["POST"])
# def redir_json():
#     """
#     Redirects a JSON post request to the Weblab JSON server.
#     This would normally not be necessary, but for now it is because
#     of different servers & cookie / routing issues.
#     """
#     core_url = flask_app.config.get("CORE_URL")
#     if core_url is None:
#         return "CORE URL WAS NOT SPECIFIED IN THE SERVER CONFIGURATION", 500
#
#     js = request.json
#     r = requests.post(core_url, data=json.dumps(js),
#                       headers={"Content-type": "application/json", "Accept": "text/plain"}, cookies=request.cookies)
#     """ @type: requests.Response """
#
#     response = Response(response=json.dumps(r.json()), status=r.status_code, mimetype="application/json", content_type="json")
#
#     # These cookies *may* be necessary due to the routing scheme used by Weblab.
#     # TODO: Remove this, if the routing scheme is ever changed.
#     response.set_cookie("weblabsessionid", r.cookies["weblabsessionid"])
#     response.set_cookie("loginweblabsessionid", r.cookies["weblabsessionid"])
#     response.set_cookie("route", r.cookies["weblabsessionid"].split(".")[1])
#     response.set_cookie("sessionid", r.cookies["weblabsessionid"].split(".")[0])
#
#     logging.debug("REDIR_JSON carried out with cookies: %r" % r.cookies)
#
#     return response
