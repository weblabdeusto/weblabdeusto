from __future__ import print_function, unicode_literals
import os
from xml.etree import ElementTree

"""
We used to use a complex XML structure in the past which nowadays we don't use anymore. 
However, for certain old operations (such as migrating old configurations to new ones),
we still need a lightweight parser of that approach. This module contains such parser.
"""

class LegacyParser(object):
    
    def _get_config_files(self, node, config_files, basedir):
        for config_node in node.findall('{http://www.weblab.deusto.es/configuration}configuration'):
            config_files.append(os.path.join(basedir, config_node.attrib['file']))

    def get_config_files(self, directory):
        config_files = []
        global_root = ElementTree.parse(os.path.join(directory, 'configuration.xml'))
        self._get_config_files(global_root, config_files, directory)

        for machine_node in global_root.findall('{http://www.weblab.deusto.es/configuration}machine'):
            machine_dir = os.path.join(directory, machine_node.text)
            machine_root = ElementTree.parse(os.path.join(machine_dir, 'configuration.xml'))
            self._get_config_files(machine_root, config_files, machine_dir)

            for instance_node in machine_root.findall('{http://www.weblab.deusto.es/configuration}instance'):
                instance_dir = os.path.join(machine_dir, instance_node.text)
                instance_root = ElementTree.parse(os.path.join(instance_dir, 'configuration.xml'))
                self._get_config_files(instance_root, config_files, instance_dir)
            
                for server_node in instance_root.findall('{http://www.weblab.deusto.es/configuration}server'):
                    server_dir = os.path.join(instance_dir, server_node.text)
                    server_root = ElementTree.parse(os.path.join(server_dir, 'configuration.xml'))
                    self._get_config_files(server_root, config_files, server_dir)

        return config_files

if __name__ == '__main__':
    files = LegacyParser().get_config_files('.')
    print(files)
    any_not_existing = False
    for f in files:
        if not os.path.exists(f):
            print("NOT EXISTING", f)
            any_not_existing = True
    if not any_not_existing:
        print("All files exist")
