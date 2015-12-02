#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
#
# Copyright (C) 2005 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
#
from __future__ import print_function, unicode_literals

import StringIO
from flask import request, jsonify

from weblab.core.web import weblab_api, get_argument
from weblab.core.codes import WEBLAB_GENERAL_EXCEPTION_CODE, PYTHON_GENERAL_EXCEPTION_CODE
import weblab.experiment.util as Util

FILE_SENT = 'file_sent'
FILE_INFO = 'file_info'
SESSION_ID = 'session_id' # for legacy code
RESERVATION_ID = 'reservation_id'
IS_ASYNC = 'is_async'

BASE_HTML_TEMPLATE="""<?xml version="1.0"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
    <head>
        <title>WebLab upload</title>
    </head>
    <body>%(MESSAGE)s</body>
</html>
"""

SUCCESS_HTML_TEMPLATE = BASE_HTML_TEMPLATE % {
		"MESSAGE" : "SUCCESS@%(RESULT)s"
	}

FAULT_HTML_TEMPLATE = BASE_HTML_TEMPLATE % {
		"MESSAGE" : "ERROR@%(THE_FAULT_CODE)s@%(THE_FAULT_MESSAGE)s"
	}

@weblab_api.route_web('/upload/', methods = ['GET', 'POST'])
def upload():
    """
    Handles file uploading. It will extract the required parameters FILE_SENT, FILE_INFO,
    SESSION_ID, and the optional parameter IS_ASYNC, and call either send_file or
    send_async_file depending on this last one.
    @return HTML defined above, with the success or failure response.
    """
    response_format = request.args.get('format', 'html').lower()
    try:
        file_info, file_sent, reservation_id, is_async = _check_arguments()
        file_content = Util.serialize(file_sent)

        weblab_api.ctx.reservation_id = reservation_id

        if not is_async:
            result = weblab_api.api.send_file(file_content, file_info)
        else:
            result = weblab_api.api.send_async_file(file_content, file_info)

    except FileUploadError as fue:
        code, message = fue.args

        if response_format == 'json':
            return jsonify(is_exception=True, message = message, code = code)
        else:
            return FAULT_HTML_TEMPLATE % {
                    'THE_FAULT_CODE' : code,
                    'THE_FAULT_MESSAGE' : message
                }
    except Exception as e:
        message = e.args[0]
        if response_format == 'json':
            return jsonify(is_exception=True, message = message, code = PYTHON_GENERAL_EXCEPTION_CODE)
        else:
            return FAULT_HTML_TEMPLATE % {
                    'THE_FAULT_CODE' : PYTHON_GENERAL_EXCEPTION_CODE,
                    'THE_FAULT_MESSAGE' : message
                }
    else:

        if not is_async:
            resultstr = result.commandstring
        else:
            resultstr = result

        print("[DBG] Returning result from file upload:", resultstr)

        if response_format == 'json':
            return jsonify(is_exception=False, result={ 'commandstring' : resultstr })
        else:
            return SUCCESS_HTML_TEMPLATE % {
                        'RESULT' : resultstr
                }

def _check_arguments():
    """
    _check_arguments()
    Retrieves the arguments which describe the file being sent.
    These areguments are the file_sent, the file-info, the sessionid, and optionally

    @return file_info, file_sent, reservation_id, is_async
    """
    file_info = get_argument(FILE_INFO)
    if file_info is None:
        raise FileUploadError(WEBLAB_GENERAL_EXCEPTION_CODE, "%s argument not provided!" % FILE_INFO)
    file_sent = request.files.get(FILE_SENT)
    if file_sent is None:
        file_sent = get_argument(FILE_SENT)
        if file_sent is None:
            raise FileUploadError(WEBLAB_GENERAL_EXCEPTION_CODE, "%s argument not provided!" % FILE_SENT)
    else:
        sio = StringIO.StringIO()
        file_sent.save(sio)
        file_sent = sio.getvalue()

    reservation_id = get_argument(RESERVATION_ID)
    if reservation_id is None:
        reservation_id = get_argument(SESSION_ID)
        if reservation_id is None:
            raise FileUploadError(WEBLAB_GENERAL_EXCEPTION_CODE, "%s argument not provided!" % ' or '.join((SESSION_ID, RESERVATION_ID)))

    # Read the IS_ASYNC parameter, which will indicate us whether we should execute the send_file asynchronously
    # or synchronously.
    is_async_str = get_argument(IS_ASYNC)
    if is_async_str is None:
        is_async = False
    else:
        is_async_str = is_async_str.lower()
        if is_async_str in ("true", "yes", "1"):
            is_async = True
        elif is_async_str in ("false", "no", "0"):
            is_async = False
        else:
            raise FileUploadError(WEBLAB_GENERAL_EXCEPTION_CODE, "%s argument is present but not valid (should be a boolean)!" % IS_ASYNC)
    return file_info, file_sent, reservation_id, is_async

class FileUploadError(Exception):
    pass

