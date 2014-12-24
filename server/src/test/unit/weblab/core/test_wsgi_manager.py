import unittest
import urllib2

from voodoo.configuration import ConfigurationManager

import test.unit.configuration as configuration_module
from test.util.module_disposer import uses_module
from test.util.ports import new as new_port
import weblab.core.wsgi_manager as wsgi_manager
import weblab.configuration_doc as configuration_doc


class HelloWorldApp(object):
    def __call__(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        yield 'Hello World\n'

class WsgiManagerTest(unittest.TestCase):
    def setUp(self):
        self.cfg_manager = ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.cfg_manager._set_value(configuration_doc.FACADE_TIMEOUT, 0.001)

        self.current_port = new_port()
        # TODO
        self.cfg_manager._set_value(configuration_doc.CORE_FACADE_JSON_PORT, self.current_port)

        app = HelloWorldApp()
        self.server = wsgi_manager.WebLabWsgiServer(self.cfg_manager,  application = app)


    @uses_module(wsgi_manager)
    def test_mofa(self):
        self.server.start()
        try:
            text = urllib2.urlopen('http://127.0.0.1:%s/' % self.current_port).read()
            self.assertEquals("Hello World\n", text)
        finally:
            self.server.stop()

def suite():
    return unittest.makeSuite(WsgiManagerTest)

if __name__ == '__main__':
    unittest.main()

