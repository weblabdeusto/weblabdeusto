#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009 University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals, 
# listed below:
#
# Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
# 

import time
from UserManager import UserManager
import urllib2
from voodoo.log import logged
import voodoo.log as log
from weblab.experiment.experiments.vm.user_manager.UserManager import PermanentConfigureError,\
    TemporaryConfigureError


HTTP_QUERY_USER_MANAGER_URL = "http_query_user_manager_url"
DEFAULT_HTTP_QUERY_USER_MANAGER_URL = "http://localhost/"


TIMES_TO_RETRY = 10
SECONDS_FOR_RETRYING = 5

class HttpQueryUserManager(UserManager):
    
    def __init__(self, cfg_manager):
        UserManager.__init__(self, cfg_manager)
        self._url = cfg_manager.get_value(HTTP_QUERY_USER_MANAGER_URL, DEFAULT_HTTP_QUERY_USER_MANAGER_URL) 


    @logged("info")
    def configure(self, sid):
        """
        Tries to configure the Virtual Machine, which in this case involves sending out
        an HTTP query with the new password to it. Because often the Virtual Machine will not
        yet be listening when this method is invoked, it will retry for a while before giving up.
        
        If the query is successfully carried out, the function returns nothing.
        If after retrying a certain number of times the VM can't be reached, or if is rached
        but the HTTP returns an error message, a ConfigureException will be raised.
        
        The ConfigureException will be either a PermanentConfigureException or a 
        TemporaryConfigureException, depending what failed. Because the configure method itself
        does already retry a fair number of times, generally even a TemporaryConfigureException
        will actually be permanent.
        """
        times_tried = 0 
        query_carried_out = False
        code = 0
        while times_tried < TIMES_TO_RETRY and not self.cancelled:
            initial_time = time.time()
            try:
                url = "%s/?sessionid=%s" % (self._url, sid)
                log.log( HttpQueryUserManager, log.LogLevel.Info, "Calling: %s" % url)
                response = urllib2.urlopen(url, timeout=50)
                code = response.read()
                log.log( HttpQueryUserManager, log.LogLevel.Info, "Configuring sessionid on VM returned: %s" % code)
                print code
                query_carried_out = True
                break
            except urllib2.HTTPError as e:
                log.log( HttpQueryUserManager, log.LogLevel.Info, "Configuring sessionid on VM returned HTTPError: %s" % e)
                times_tried += 1
            except urllib2.URLError as e:
                log.log( HttpQueryUserManager, log.LogLevel.Info, "Configuring sessionid on VM returned URLError: %s" % e)
                # These are timeout errors which occur when the virtual OS takes too long to start, which is
                # actually quite common.
                # The above error has the following tuple as its args: (error(10060, 'Operation timed out'),)
                times_tried += 1
            except Exception as e:
                log.log( HttpQueryUserManager, log.LogLevel.Info, "Configuring sessionid on VM returned unexpected Exception: %s" % e)
                # Unknown exception, we better consider it permanent straightaway.
                raise PermanentConfigureError()
            final_time = time.time()
            time_elapsed = final_time - initial_time
            if SECONDS_FOR_RETRYING - time_elapsed > 0:
                time.sleep(SECONDS_FOR_RETRYING - time_elapsed)
                
            
        # We have either succeeded or retried for the maximum number of times. 
        # If we did not succeed, report through an exception.
        if not query_carried_out:
            # The server did not respond. Maybe it is still loading and we did not retry enough
            # times.
            raise TemporaryConfigureError()
        
        # We managed to send the query but the server reported some kind of error.
        # TODO: Send Permanent instead of Temporary depending on the error.
        if code != 'ok':
            raise TemporaryConfigureError("Unexpected code returned: %s" % code)
