import json
import unittest

from mock import patch

from voodoo.gen2 import CoordAddress, Locator, load, CORE_CLASS, LAB_CLASS


class LoaderTest(unittest.TestCase):
    def test_load(self):
        result = load('test/unit/voodoo/gen2/sample.yml')
        machine = result['core_machine']
        config_files = ['core_machine/machine_config.py', 'core_machine/machine_config.py']
        self.assertEquals(machine.config_files, config_files)
        self.assertEquals(machine.host, '192.168.0.1')

        core_server1 = machine['core_server1']
        core_component = core_server1['core']
        self.assertEquals(core_component.config_values['core_facade_port'], 10000)
        self.assertEquals(core_component.component_type, 'core')
        self.assertEquals(core_component.component_class, CORE_CLASS)
        self.assertEquals(len(core_component.protocols), 0)

        laboratory1 = machine['laboratory1']
        lab_component1 = laboratory1['laboratory1']

        self.assertEquals(lab_component1.config_files, ['core_machine/laboratory1/laboratory1/server_config.py'])
        self.assertEquals(lab_component1.component_type, 'laboratory')
        self.assertEquals(lab_component1.component_class, LAB_CLASS)
        self.assertEquals(lab_component1.protocols.port, 10003)
        self.assertEquals(lab_component1.protocols['http'], {})
        self.assertEquals(lab_component1.protocols['xmlrpc'], {})

        lab_address1 = CoordAddress('core_machine', 'laboratory1', 'laboratory1')
        lab_address2 = CoordAddress('core_machine', 'laboratory2', 'laboratory2')
        lab_component1_obtained = result[lab_address1]
        lab_component2_obtained = result[lab_address2]

        self.assertEquals(lab_component1_obtained, lab_component1)
        self.assertNotEquals(lab_component2_obtained, lab_component1)

class LocatorTest(unittest.TestCase):

    @patch('voodoo.log.log')
    def test_find_labs(self, voodoo_log):
        global_config = load('test/unit/voodoo/gen2/sample.yml')
        core_server = CoordAddress('core_machine', 'core_server1', 'core')
        locator = Locator(global_config, core_server)

        self.assertFalse(voodoo_log.called)
        laboratories = locator.find_by_type('laboratory')
        self.assertTrue(voodoo_log.called)

        self.assertEquals(len(laboratories), 5)
        
        t = CoordAddress.translate_address

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
                    addresses['%s:%s@%s' % (host, process, component)] = CoordAddress(host, process, component)
        
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

class ClientTest(unittest.TestCase):
    def test_client(self):
        pass

if __name__ == '__main__':
    unittest.main()
