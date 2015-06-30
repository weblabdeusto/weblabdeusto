from __future__ import print_function, unicode_literals
import unittest
import requests
import time

from voodoo.configuration import ConfigurationManager

import test.unit.configuration as configuration_module
from test.util.module_disposer import uses_module
from test.util.ports import new as new_port
import weblab.core.wsgi_manager as wsgi_manager
import weblab.configuration_doc as configuration_doc


class HelloWorldApp(object):
    def __call__(self, environ, start_response):
        start_response(str('200 OK'), [(str('Content-Type'), str('text/plain'))])
        yield str('Hello World\n')

class WsgiManagerTest(unittest.TestCase):
    def setUp(self):
        self.cfg_manager = ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.cfg_manager._set_value(configuration_doc.FACADE_TIMEOUT, 0.001)

        self.current_port = new_port()
        self.cfg_manager._set_value(configuration_doc.CORE_FACADE_PORT, self.current_port)

        app = HelloWorldApp()
        self.server = wsgi_manager.WebLabWsgiServer(self.cfg_manager,  application = app)


    @uses_module(wsgi_manager)
    def test_server(self):
        self.server.start()
        try:
            time.sleep(0.1)
            text = requests.get('http://127.0.0.1:%s/' % self.current_port, timeout = 10).text
            self.assertEquals("Hello World\n", text)
        finally:
            self.server.stop()

def suite():
    return unittest.makeSuite(WsgiManagerTest)

if __name__ == '__main__':
    unittest.main()

