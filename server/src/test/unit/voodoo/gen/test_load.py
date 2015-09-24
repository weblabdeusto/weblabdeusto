from __future__ import print_function, unicode_literals
import json
import unittest

from mock import patch

import voodoo.gen as gen
import voodoo.gen.clients as clients
import voodoo.gen.registry as registry
import voodoo.gen.util as util
import voodoo.gen.parser as parser

from voodoo.gen.exc import InternalCapturedServerCommunicationError
import test.util.ports as ports


class LoaderTest(unittest.TestCase):
    def test_load(self):
        result = gen.load('test/unit/voodoo/gen/sample.yml')
        machine = result['core_machine']
        config_files = ['test/unit/voodoo/gen/core_machine/machine_config.py', 'test/unit/voodoo/gen/core_machine/machine_config.py']
        self.assertEquals(machine.config_files, config_files)
        self.assertEquals(machine.host, '192.168.0.1')
        self.assertEquals(machine.runner, 'run.py')

        core_server1 = machine['core_server1']
        core_component = core_server1['core']
        self.assertEquals(core_component.config_values['core_facade_port'], 10000)
        self.assertEquals(core_component.component_type, 'core')
        self.assertEquals(core_component.component_class, parser.CORE_CLASS)
        self.assertEquals(len(core_component.protocols), 0)

        laboratory1 = machine['laboratory1']
        lab_component1 = laboratory1['laboratory1']

        self.assertEquals(lab_component1.config_files, ['test/unit/voodoo/gen/core_machine/laboratory1/laboratory1/server_config.py'])
        self.assertEquals(lab_component1.component_type, 'laboratory')
        self.assertEquals(lab_component1.component_class, parser.LAB_CLASS)
        self.assertEquals(lab_component1.protocols.port, 10003)
        self.assertEquals(lab_component1.protocols['http'], {})
        self.assertEquals(lab_component1.protocols['xmlrpc'], {})

        lab_address1 = gen.CoordAddress('core_machine', 'laboratory1', 'laboratory1')
        lab_address2 = gen.CoordAddress('core_machine', 'laboratory2', 'laboratory2')
        lab_component1_obtained = result[lab_address1]
        lab_component2_obtained = result[lab_address2]

        self.assertEquals(lab_component1_obtained, lab_component1)
        self.assertNotEquals(lab_component2_obtained, lab_component1)

class LocatorTest(unittest.TestCase):

    @patch('voodoo.log.log')
    def test_find_labs(self, voodoo_log):
        global_config = gen.load('test/unit/voodoo/gen/sample.yml')
        core_server = gen.CoordAddress('core_machine', 'core_server1', 'core')
        locator = gen.Locator(global_config, core_server)

        self.assertFalse(voodoo_log.called)
        laboratories = locator.find_by_type('laboratory')
        self.assertTrue(voodoo_log.called)

        self.assertEquals(len(laboratories), 5)
        
        t = gen.CoordAddress.translate

        self.assertTrue(t('laboratory:laboratory@accessible_machine') in laboratories)
        self.assertTrue(t('laboratory3:core_server1@core_machine') in laboratories)
        self.assertTrue(t('laboratory1:laboratory1@core_machine') in laboratories)
        self.assertTrue(t('laboratory2:laboratory2@core_machine') in laboratories)

        con1 = locator.get_connection(t('laboratory:laboratory@accessible_machine'))
        self.assertDictEquals(con1, {'type' : 'http', 'host' : '192.168.0.2', 'port' : 12345, 'path' : '' })

        con2 = locator.get_connection(t('laboratory3:core_server1@core_machine'))
        self.assertDictEquals(con2, {'type' : 'direct', 'address' : 'laboratory3:core_server1@core_machine'})

        con3 = locator.get_connection(t('laboratory1:laboratory1@core_machine'))
        self.assertDictEquals(con3, {'type' : 'http', 'host' : '127.0.0.1', 'port' : 10003, 'path' : '' })

        con4 = locator.get_connection(t('laboratory2:laboratory2@core_machine'))
        self.assertDictEquals(con4, {'type' : 'xmlrpc', 'host' : '127.0.0.1', 'port' : 10004, 'path' : '' })


    def assertDictEquals(self, dict1, dict2):
        self.assertEquals(json.dumps(dict1), json.dumps(dict2))


class CoordAddressTest(unittest.TestCase):
    def test_general(self):
        addresses = {}
        for host in 'host1', 'host2':
            for process in 'process1', 'process2':
                for component in 'component1', 'component2':
                    addresses['%s:%s@%s' % (host, process, component)] = gen.CoordAddress(host, process, component)
        
        self.assertEquals(len(addresses), 8)

        operations = 0

        for key1, value1 in addresses.iteritems():
            for key2, value2 in addresses.iteritems():
                operations += 1
                new_key1 = value1.host + value1.process + value1.component
                new_key2 = value2.host + value2.process + value2.component
                if key1 == key2:
                    # Assert they're equal
                    self.assertTrue(value1 == value2)
                    self.assertFalse(value1 != value2)
                    self.assertEquals(cmp(value1, value2), 0)
                    self.assertEquals(unicode(value1), unicode(value2))
                    self.assertEquals(hash(value1), hash(value2))
                    self.assertEquals(repr(value1), repr(value2))
                    self.assertEquals(value1.address, value2.address)
                    self.assertEquals(new_key1, new_key2)
                else:
                    # Assert they're not equal
                    self.assertFalse(value1 == value2)
                    self.assertTrue(value1 != value2)
                    self.assertNotEquals(cmp(value1, value2), 0)
                    self.assertNotEquals(unicode(value1), unicode(value2))
                    self.assertNotEquals(hash(value1), hash(value2))
                    self.assertNotEquals(repr(value1), repr(value2))
                    self.assertNotEquals(value1.address, value2.address)
                    self.assertNotEquals(new_key1, new_key2)

        # paranoid mode: things are being tested ;-)
        self.assertEquals(operations, 64)

class UtilsTest(unittest.TestCase):

    def test_type_serialization(self):
        key_error_str = util._get_type_name(KeyError)
        self.assertEquals(util._load_type(key_error_str), KeyError)


sample_configuration = """
hosts:
    main_host:
        host: 127.0.0.1
        processes:
            core:
                components:
                    core:
                        type: core
                    lab:
                        type: laboratory
            lab:
                components: 
                    lab1:
                        type: laboratory
                        protocols:
                            port: %(PORT1)s
                    lab2:
                        type: laboratory
                        protocols:
                            port: %(PORT2)s
                            supports: xmlrpc
"""

class methods(object):
    core = []
    laboratory = ['testing_lab']

class FakeLaboratoryServer(object):
    def __init__(self, *args, **kwargs):
        pass

    def do_testing_lab(self, a, b):
        if a == 0 and b == 0:
            raise FakeError("testing")
        return a / b

class FakeCoreServer(object):
    def __init__(self, *args, **kwargs):
        pass

class FakeError(Exception):
    pass

class CommunicationsTest(unittest.TestCase):

    def setUp(self):
        registry.GLOBAL_REGISTRY.clear()
        self.original_methods_path = util.METHODS_PATH
        self.original_lab_class = parser.LAB_CLASS
        self.original_core_class = parser.CORE_CLASS
       
        clients.ACCEPTABLE_EXC_TYPES = clients.ACCEPTABLE_EXC_TYPES + ('test.','__main__.')
        parser.LAB_CLASS = FakeLaboratoryServer.__module__ + '.' + FakeLaboratoryServer.__name__
        parser.CORE_CLASS = FakeCoreServer.__module__ + '.' + FakeCoreServer.__name__
        util.METHODS_PATH = CommunicationsTest.__module__

        lab_port1 = ports.new()
        lab_port2 = ports.new()
        
        self.core_addr = gen.CoordAddress.translate('core:core@main_host')
        self.lab_addr1 = gen.CoordAddress.translate('lab:core@main_host')
        self.lab_addr2 = gen.CoordAddress.translate('lab1:lab@main_host')
        self.lab_addr3 = gen.CoordAddress.translate('lab2:lab@main_host')

        config_str = sample_configuration % { 'PORT1' : lab_port1, 'PORT2' : lab_port2 }
        self.global_config = gen.loads(config_str)

        process1 = self.global_config.load_process('main_host', 'core')
        process2 = self.global_config.load_process('main_host', 'lab')

        self.processes = [ process1, process2 ]

    def tearDown(self):
        for process in self.processes:
            process.stop()

        util.METHODS_PATH = self.original_methods_path
        parser.LAB_CLASS = self.original_lab_class
        parser.CORE_CLASS = self.original_core_class
        registry.GLOBAL_REGISTRY.clear()

    def test_correct_methods(self):
        locator = gen.Locator(self.global_config, self.core_addr)

        self.assertEquals(locator[self.lab_addr1].testing_lab(10, 5), 2)
        self.assertEquals(locator[self.lab_addr2].testing_lab(10, 5), 2)
        self.assertEquals(locator[self.lab_addr3].testing_lab(10, 5), 2)

    def test_external_error_methods(self):
        locator = gen.Locator(self.global_config, self.core_addr)

        self.assertRaises(InternalCapturedServerCommunicationError, locator[self.lab_addr1].testing_lab, 10, 0)
        self.assertRaises(InternalCapturedServerCommunicationError, locator[self.lab_addr2].testing_lab, 10, 0)
        self.assertRaises(InternalCapturedServerCommunicationError, locator[self.lab_addr3].testing_lab, 10, 0)

    def test_acceptable_error_methods(self):
        locator = gen.Locator(self.global_config, self.core_addr)

        self.assertRaises(FakeError, locator[self.lab_addr1].testing_lab, 0, 0)
        self.assertRaises(FakeError, locator[self.lab_addr2].testing_lab, 0, 0)
        # In XML-RPC, it's not propagated
        self.assertRaises(InternalCapturedServerCommunicationError, locator[self.lab_addr3].testing_lab, 0, 0)

def suite():
    return unittest.makeSuite(LoaderTest)

if __name__ == '__main__':
    unittest.main()
