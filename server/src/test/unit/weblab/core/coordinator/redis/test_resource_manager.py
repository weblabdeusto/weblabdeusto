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
#
from __future__ import print_function, unicode_literals

try:
    import redis
except ImportError:
    REDIS_AVAILABLE = False
else:
    REDIS_AVAILABLE = True

import unittest

import test.unit.configuration as configuration_module
import voodoo.configuration as ConfigurationManager

from weblab.data.experiments import ExperimentInstanceId

from weblab.data.experiments import ExperimentId
from weblab.core.coordinator.resource import Resource
import weblab.core.coordinator.redis.resource_manager as ResourcesManager
import weblab.core.coordinator.exc as CoordExc

class ResourcesManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg_manager = ConfigurationManager.ConfigurationManager()
        self.cfg_manager.append_module(configuration_module)

        self.pool = redis.ConnectionPool()
        redis_maker = lambda : redis.Redis(connection_pool = self.pool)
        self.resources_manager = ResourcesManager.ResourcesManager(redis_maker)
        self.resources_manager._clean()

    def tearDown(self):
        self.pool.disconnect()

    def test_add_resource(self):
        self.assertEquals([], self.resources_manager.list_resources())
        self.resources_manager.add_resource(Resource("type", "instance"))
        self._check_resource_added()

        # Can be executed twice without conflicts

        self.resources_manager.add_resource(Resource("type", "instance"))
        self._check_resource_added()

    def _check_resource_added(self):
        resources = self.resources_manager.list_resource_instances()
        self.assertEquals(1, len(resources))

        resource = resources[0]
        self.assertEquals("type", resource.resource_type)

        self.assertEquals('instance', resource.resource_instance)

        # TODO XXX 
        # slot = resource_instance.slot
        # self.assertNotEquals(None, slot)
        # self.assertEquals(resource_instance, slot.resource_instance)

    def _check_experiment_instance_id_added(self):
        experiment_types = self.resources_manager.list_experiments()
        self.assertEquals(1, len(experiment_types))

        experiment_type = experiment_types[0]
        self.assertEquals("PLD Experiments", experiment_type.cat_name)
        self.assertEquals("ud-pld", experiment_type.exp_name)

        experiment_instances = self.resources_manager.list_experiment_instances_by_type(experiment_type)
        self.assertEquals(1, len(experiment_instances))

        experiment_instance = experiment_instances[0]
        self.assertEquals("exp1", experiment_instance.inst_name)
        self.assertEquals(experiment_type, experiment_instance.to_experiment_id())

        resource_instance = self.resources_manager.get_resource_instance_by_experiment_instance_id(experiment_instance)
        self.assertEquals("instance", resource_instance.resource_instance)

        resource_type = resource_instance.resource_type

        retrieved_resource_types = self.resources_manager.get_resource_types_by_experiment_id(experiment_type)
        self.assertTrue(resource_type in retrieved_resource_types)

        retrieved_experiment_instance_ids = self.resources_manager.list_experiment_instance_ids_by_resource_type(resource_type)
        self.assertTrue(experiment_instance in retrieved_experiment_instance_ids)


    def test_add_experiment_instance_id(self):

        self.assertEquals([], self.resources_manager.list_resources())

        exp_id = ExperimentInstanceId("exp1","ud-pld","PLD Experiments")

        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_id, Resource("type", "instance"))
        
        self._check_resource_added()
        self._check_experiment_instance_id_added()

    def test_add_experiment_instance_id_redundant(self):

        self.assertEquals([], self.resources_manager.list_resources())

        exp_id = ExperimentInstanceId("exp1","ud-pld","PLD Experiments")

        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_id, Resource("type", "instance"))

        # No problem in adding twice the same
        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_id, Resource("type", "instance"))
        
        # Everything is all right
        self._check_resource_added()
        self._check_experiment_instance_id_added()

        # However, we can't add another time the same experiment instance with a different laboratory id:
        self.assertRaises(CoordExc.InvalidExperimentConfigError,
                self.resources_manager.add_experiment_instance_id,
                "laboratory2:WL_SERVER1@WL_MACHINE1", exp_id, Resource("type", "instance"))

        # Or the same experiment instance with a different resource instance:
        self.assertRaises(CoordExc.InvalidExperimentConfigError,
                self.resources_manager.add_experiment_instance_id,
                "laboratory1:WL_SERVER1@WL_MACHINE1", exp_id, Resource("type", "instance2"))


    def test_get_resource_instance_by_experiment_instance_id(self):
        exp_id = ExperimentInstanceId("exp1","ud-pld","PLD Experiments")
        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_id, Resource("type", "instance"))

        resource = self.resources_manager.get_resource_instance_by_experiment_instance_id(exp_id)
        expected_resource = Resource("type", "instance")
        self.assertEquals(expected_resource, resource)

    def test_get_resource_instance_by_experiment_instance_id_failing(self):
        exp_id = ExperimentInstanceId("exp1","ud-pld","PLD Experiments")
        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_id, Resource("type", "instance"))

        exp_invalid_type = ExperimentInstanceId("exp1","ud-pld.invalid", "PLD Experiments")

        self.assertRaises( CoordExc.ExperimentNotFoundError,
                            self.resources_manager.get_resource_instance_by_experiment_instance_id,
                            exp_invalid_type )

        exp_invalid_inst = ExperimentInstanceId("exp.invalid","ud-pld", "PLD Experiments")
        self.assertRaises( CoordExc.ExperimentNotFoundError,
                            self.resources_manager.get_resource_instance_by_experiment_instance_id,
                            exp_invalid_inst )

    def test_get_resource_types_by_experiment_id(self):
        exp_id = ExperimentInstanceId("exp1","ud-pld","PLD Experiments")
        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_id, Resource("type", "instance"))

        exp_type_id = ExperimentId("ud-pld", "PLD Experiments")
        resource_types = self.resources_manager.get_resource_types_by_experiment_id(exp_type_id)
        self.assertEquals(1, len(resource_types))
        self.assertTrue(u"type" in resource_types)

    def test_get_resource_types_by_experiment_id_error(self):
        exp_id = ExperimentInstanceId("exp1","ud-pld","PLD Experiments")
        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_id, Resource("type", "instance"))

        self.assertRaises(
                CoordExc.ExperimentNotFoundError,
                self.resources_manager.get_resource_types_by_experiment_id,
                ExperimentId("foo","bar")
            )

    def test_remove_resource_instance_id(self):
        exp_id = ExperimentInstanceId("exp1","ud-pld","PLD Experiments")
        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_id, Resource("type", "instance"))

        experiment_instances = self.resources_manager.list_experiment_instances_by_type(exp_id.to_experiment_id())
        self.assertEquals(1, len(experiment_instances))

        self.resources_manager.remove_resource_instance_id(exp_id)

        experiment_instances = self.resources_manager.list_experiment_instances_by_type(exp_id.to_experiment_id())
        self.assertEquals(0, len(experiment_instances))

    def test_remove_resource_instance(self):
        exp_id = ExperimentInstanceId("exp1","ud-pld","PLD Experiments")
        resource_instance = Resource("type", "instance")
        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_id, resource_instance)

        # Checking that the resources are there
        experiment_instances = self.resources_manager.list_experiment_instances_by_type(exp_id.to_experiment_id())
        self.assertEquals(1, len(experiment_instances))
        resource_instances = self.resources_manager.list_resource_instances()
        self.assertEquals(1, len(resource_instances))

        # Removing resource instance
        self.resources_manager.remove_resource_instance(resource_instance)

        # Checking that the resources are not there, neither the experiment instances
        resource_instances = self.resources_manager.list_resource_instances()
        self.assertEquals(0, len(resource_instances))
        experiment_instances = self.resources_manager.list_experiment_instances_by_type(exp_id.to_experiment_id())
        self.assertEquals(0, len(experiment_instances))

    def test_list_resources(self):
        exp_id1 = ExperimentInstanceId("exp1","ud-pld","PLD Experiments")
        resource_instance1 = Resource("type1", "instance1")
        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_id1, resource_instance1)

        exp_id2 = ExperimentInstanceId("exp2","ud-pld","PLD Experiments")
        resource_instance2 = Resource("type2", "instance1")
        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_id2, resource_instance2)

        resources = self.resources_manager.list_resources()
        self.assertEquals(2, len(resources))
        self.assertTrue('type1' in resources)
        self.assertTrue('type2' in resources)

    def test_list_experiments(self):
        exp_id1 = ExperimentInstanceId("exp1","ud-pld","PLD Experiments")
        resource_instance1 = Resource("type1", "instance1")
        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_id1, resource_instance1)

        exp_id2 = ExperimentInstanceId("exp2","ud-pld","PLD Experiments")
        resource_instance2 = Resource("type2", "instance1")
        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_id2, resource_instance2)

        resources = self.resources_manager.list_experiments()
        self.assertEquals(1, len(resources))
        self.assertTrue(ExperimentId('ud-pld', 'PLD Experiments') in resources)

    def test_list_experiment_instance_ids_by_resource(self):
        exp_id1 = ExperimentInstanceId("exp1","ud-pld","PLD Experiments")
        resource_instance1 = Resource("type1", "instance1")
        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_id1, resource_instance1)

        exp_id2 = ExperimentInstanceId("exp2","ud-pld","PLD Experiments")
        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_id2, resource_instance1)

        exp_id3 = ExperimentInstanceId("exp3","ud-pld","PLD Experiments")
        resource_instance2 = Resource("type1", "instance2")
        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_id3, resource_instance2)

        experiment_instance_ids = self.resources_manager.list_experiment_instance_ids_by_resource(resource_instance1)
        self.assertEquals(2, len(experiment_instance_ids))

        self.assertTrue(ExperimentInstanceId('exp1','ud-pld', 'PLD Experiments') in experiment_instance_ids)
        self.assertTrue(ExperimentInstanceId('exp2','ud-pld', 'PLD Experiments') in experiment_instance_ids)


    def test_list_laboratories_addresses(self):
        exp_id1 = ExperimentInstanceId("exp1","ud-pld","PLD Experiments")
        resource_instance1 = Resource("type1", "instance1")
        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_id1, resource_instance1)

        # Repeating laboratory1, but a set is returned so no problem
        exp_id2 = ExperimentInstanceId("exp2","ud-pld","PLD Experiments")
        resource_instance2 = Resource("type2", "instance1")
        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_id2, resource_instance2)

        exp_id3 = ExperimentInstanceId("exp3","ud-pld","PLD Experiments")
        resource_instance3 = Resource("type2", "instance2")
        self.resources_manager.add_experiment_instance_id("laboratory2:WL_SERVER1@WL_MACHINE1", exp_id3, resource_instance3)

        addresses = self.resources_manager.list_laboratories_addresses()
        self.assertEquals(2, len(addresses))
        self.assertTrue("laboratory1:WL_SERVER1@WL_MACHINE1" in addresses)
        self.assertEquals(2, len(addresses["laboratory1:WL_SERVER1@WL_MACHINE1"]))
        self.assertTrue(exp_id1 in addresses["laboratory1:WL_SERVER1@WL_MACHINE1"])
        self.assertTrue(exp_id2 in addresses["laboratory1:WL_SERVER1@WL_MACHINE1"])
        self.assertTrue("laboratory2:WL_SERVER1@WL_MACHINE1" in addresses)
        self.assertEquals(1, len(addresses["laboratory2:WL_SERVER1@WL_MACHINE1"]))
        self.assertTrue(exp_id3 in addresses["laboratory2:WL_SERVER1@WL_MACHINE1"])

        self.assertEquals(resource_instance1, addresses["laboratory1:WL_SERVER1@WL_MACHINE1"][exp_id1])
        self.assertEquals(resource_instance2, addresses["laboratory1:WL_SERVER1@WL_MACHINE1"][exp_id2])
        self.assertEquals(resource_instance3, addresses["laboratory2:WL_SERVER1@WL_MACHINE1"][exp_id3])

    def test_scheduler_reservation_associations(self):
        exp_inst_id1  = ExperimentInstanceId("exp1","ud-pld",  "PLD experiments")
        exp_inst_id1b = ExperimentInstanceId("exp2","ud-pld",  "PLD experiments")
        exp_inst_id2  = ExperimentInstanceId("exp1","ud-fpga", "FPGA experiments")

        exp_id1 = exp_inst_id1.to_experiment_id()
        exp_id2 = exp_inst_id2.to_experiment_id()

        self.resources_manager.add_resource(Resource("pld_local", "instance"))
        self.resources_manager.add_resource(Resource("pld_remote", "instance"))
        self.resources_manager.add_resource(Resource("fpga_remote", "instance"))

        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_inst_id1, Resource("pld_local",  "instance"))
        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_inst_id1b, Resource("pld_remote", "instance"))
        self.resources_manager.add_experiment_instance_id("laboratory1:WL_SERVER1@WL_MACHINE1", exp_inst_id2, Resource("fpga_remote", "instance"))

        reservation1 = 'reservation1'
        reservation2 = 'reservation2'

        self.resources_manager.associate_scheduler_to_reservation(reservation1, exp_id1, 'pld_local')
        self.resources_manager.associate_scheduler_to_reservation(reservation1, exp_id1, 'pld_remote')
        self.resources_manager.associate_scheduler_to_reservation(reservation2, exp_id2, 'fpga_remote')

        resource_type_names = self.resources_manager.retrieve_schedulers_per_reservation(reservation1, exp_id1)
        self.assertEquals(set(('pld_local','pld_remote')), set(resource_type_names))
        resource_type_names = self.resources_manager.retrieve_schedulers_per_reservation(reservation2, exp_id2)
        self.assertEquals(['fpga_remote'], list(resource_type_names))

        self.resources_manager.dissociate_scheduler_from_reservation(reservation1, exp_id1, 'pld_remote')
        resource_type_names = self.resources_manager.retrieve_schedulers_per_reservation(reservation1, exp_id1)
        self.assertEquals(['pld_local'], list(resource_type_names))

        self.resources_manager.clean_associations_for_reservation(reservation1, exp_id1)

        resource_type_names = self.resources_manager.retrieve_schedulers_per_reservation(reservation1, exp_id1)
        self.assertEquals(0, len(resource_type_names))


if REDIS_AVAILABLE:
    def suite():
        return unittest.makeSuite(ResourcesManagerTestCase)

if __name__ == '__main__':
    unittest.main()

