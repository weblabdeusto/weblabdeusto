import unittest

from voodoo.gen2 import CoordAddress, Locator, load, CORE_CLASS, LAB_CLASS


class LoadTest(unittest.TestCase):
    def test_load(self):
        result = load('test/unit/voodoo/gen2/sample.yml')
        machine = result['core_machine']
        config_files = ['core_machine/machine_config.py', 'core_machine/machine_config.py']
        self.assertEquals(machine.config_files, config_files)
        self.assertEquals(machine.host, '127.0.0.1')

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


if __name__ == '__main__':
    unittest.main()
