from __future__ import print_function, unicode_literals
import os
import json

from flask import make_response
from weblab.util import data_filename
from weblab.core.wl import weblab_api

@weblab_api.route_web('/version.js')
def version():
    filename = data_filename(os.path.join('weblab','version.json'))
    contents = None

    if filename is not None and os.path.exists(filename):
        version_contents = open(filename).read()
        try:
            version_contents_value = json.loads(version_contents)
        except Exception:
            pass
        else:
            message = r"""WebLab-Deusto r<a href=\"https://github.com/weblabdeusto/weblabdeusto/commits/{version}\">{number}</a> | Last update: {date}""".format(
                version = version_contents_value['version'],
                number = version_contents_value['version_number'],
                date = version_contents_value['date']
            )
            contents = 'var weblab_version = %s;\nvar wlVersionMessage = "%s";' % (version_contents, message)

    if contents is None:
        contents = 'var weblab_version = {};\nvar wlVersionMessage = null;'

    response = make_response(contents)
    response.content_type = 'text/javascript';
    return response

