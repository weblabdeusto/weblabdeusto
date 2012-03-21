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

from weblab.comm.codes import WEBLAB_GENERAL_EXCEPTION_CODE, PYTHON_GENERAL_EXCEPTION_CODE
from voodoo.sessions.session_id import SessionId
import weblab.comm.web_server as WebFacadeServer
import weblab.experiment.util as Util

FILE_SENT = 'file_sent'
FILE_INFO = 'file_info'
SESSION_ID = 'session_id'
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

class FileUploadMethod(WebFacadeServer.Method):
    path = '/upload/'

    def run(self):
        """
        run()
        Handles file uploading. It will extract the required parameters FILE_SENT, FILE_INFO,
        SESSION_ID, and the optional parameter IS_ASYNC, and call either send_file or
        send_async_file depending on this last one.
        @return HTML defined above, with the success or failure response.
        """
        try:
            file_info, file_sent, session_id, is_async = self._check_arguments()
            file_content = Util.serialize(file_sent)
            sid = SessionId(session_id)

            if(not is_async):
                result = self.server.send_file(sid, file_content, file_info)
            else:
                result = self.server.send_async_file(sid, file_content, file_info)

        except FileUploadError as fue:
            code, message = fue.args
            return FAULT_HTML_TEMPLATE % {
                        'THE_FAULT_CODE' : code,
                        'THE_FAULT_MESSAGE' : message
                    }
        except Exception as e:
            message = e.args[0]
            return FAULT_HTML_TEMPLATE % {
                        'THE_FAULT_CODE' : PYTHON_GENERAL_EXCEPTION_CODE,
                        'THE_FAULT_MESSAGE' : message
                    }
        else:

            if not is_async:
                resultstr = result.commandstring
            else:
                resultstr = result

            print "[DBG] Returning result from file upload: " + resultstr

            return SUCCESS_HTML_TEMPLATE % {
                            'RESULT' : resultstr
                    }

    def _check_arguments(self):
        """
        _check_arguments()
        Retrieves the arguments which describe the file being sent.
        These areguments are the file_sent, the file-info, the sessionid, and optionally
        @return file_info, file_sent, session_id, is_async
        """
        file_info = self.get_argument(FILE_INFO)
        if file_info is None:
            raise FileUploadError(WEBLAB_GENERAL_EXCEPTION_CODE, "%s argument not provided!" % FILE_INFO)
        file_sent = self.get_argument(FILE_SENT)
        if file_sent is None:
            raise FileUploadError(WEBLAB_GENERAL_EXCEPTION_CODE, "%s argument not provided!" % FILE_SENT)
        session_id = self.get_argument(SESSION_ID)
        if session_id is None:
            raise FileUploadError(WEBLAB_GENERAL_EXCEPTION_CODE, "%s argument not provided!" % SESSION_ID)

        # Read the IS_ASYNC parameter, which will indicate us whether we should execute the send_file asynchronously
        # or synchronously.
        is_async_str = self.get_argument(IS_ASYNC)
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
        return file_info, file_sent, session_id, is_async

class FileUploadError(Exception):
    pass

