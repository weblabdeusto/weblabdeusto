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

import json

from weblab.data.experiments import ExperimentId, ExperimentInstanceId
from weblab.core.coordinator.resource import Resource
import weblab.core.coordinator.exc as CoordExc

from voodoo.typechecker import typecheck

from weblab.core.coordinator.redis.constants import (
    WEBLAB_EXPERIMENT_TYPES,
    WEBLAB_EXPERIMENT_RESOURCES,
    WEBLAB_EXPERIMENT_INSTANCES,
    WEBLAB_EXPERIMENT_INSTANCE,

    WEBLAB_RESOURCES,
    WEBLAB_RESOURCE,
    WEBLAB_RESOURCE_SLOTS,
    WEBLAB_RESOURCE_WORKING,
    WEBLAB_RESOURCE_EXPERIMENTS,
    WEBLAB_RESOURCE_RESERVATIONS,
    WEBLAB_RESOURCE_INSTANCE_EXPERIMENTS,
    WEBLAB_RESERVATIONS_ACTIVE_SCHEDULERS,

    LAB_COORD,
    RESOURCE_INST,
    EXPERIMENT_TYPE,
    RESOURCE_TYPE,
)

class ResourcesManager(object):
    def __init__(self, redis_maker):
        self._redis_maker = redis_maker

    @typecheck(Resource)
    def add_resource(self, resource):
        client = self._redis_maker()
        client.sadd(WEBLAB_RESOURCES, resource.resource_type)
        client.sadd(WEBLAB_RESOURCE % resource.resource_type,         resource.resource_instance)
        client.sadd(WEBLAB_RESOURCE_SLOTS   % resource.resource_type, resource.resource_instance)
        client.sadd(WEBLAB_RESOURCE_WORKING % resource.resource_type, resource.resource_instance)
        
    @typecheck(ExperimentId, basestring)
    def add_experiment_id(self, experiment_id, resource_type):
        client = self._redis_maker()
        client.sadd(WEBLAB_RESOURCES, resource_type)
        client.sadd(WEBLAB_EXPERIMENT_TYPES, experiment_id.to_weblab_str())
    
    @typecheck(basestring, ExperimentInstanceId, Resource)
    def add_experiment_instance_id(self, laboratory_coord_address, experiment_instance_id, resource):
        self.add_resource(resource)

        experiment_id     = experiment_instance_id.to_experiment_id()
        experiment_id_str = experiment_id.to_weblab_str()

        self.add_experiment_id(experiment_id, resource.resource_type)

        client = self._redis_maker()
        client.sadd(WEBLAB_EXPERIMENT_INSTANCES % experiment_id_str, experiment_instance_id.inst_name)

        weblab_experiment_instance = WEBLAB_EXPERIMENT_INSTANCE % (experiment_id_str, experiment_instance_id.inst_name)

        weblab_resource_experiments = WEBLAB_RESOURCE_EXPERIMENTS % resource.resource_type
        client.sadd(weblab_resource_experiments, experiment_id_str)
        
        weblab_experiment_resources = WEBLAB_EXPERIMENT_RESOURCES % experiment_id_str
        client.sadd(weblab_experiment_resources, resource.resource_type)

        weblab_resource_instance_experiments = WEBLAB_RESOURCE_INSTANCE_EXPERIMENTS % (resource.resource_type, resource.resource_instance)
        client.sadd(weblab_resource_instance_experiments, experiment_instance_id.to_weblab_str())

        retrieved_laboratory_coord_address = client.hget(weblab_experiment_instance, LAB_COORD)
        if retrieved_laboratory_coord_address is not None: 
            if retrieved_laboratory_coord_address != laboratory_coord_address:
                raise CoordExc.InvalidExperimentConfigError("Attempt to register the experiment %s in the laboratory %s; this experiment is already registered in the laboratory %s" % (experiment_instance_id, laboratory_coord_address, retrieved_laboratory_coord_address))

        client.hset(weblab_experiment_instance, LAB_COORD, laboratory_coord_address)

        retrieved_weblab_resource_instance = client.hget(weblab_experiment_instance, RESOURCE_INST)

        if retrieved_weblab_resource_instance is not None:
            if retrieved_weblab_resource_instance != resource.to_weblab_str():
                    raise CoordExc.InvalidExperimentConfigError("Attempt to register the experiment %s with resource %s when it was already bound to resource %s" % (experiment_instance_id, resource, retrieved_weblab_resource_instance))

        client.hset(weblab_experiment_instance, RESOURCE_INST, resource.to_weblab_str())

    @typecheck(Resource)
    def acquire_resource(self, current_resource):
        weblab_resource_slots = WEBLAB_RESOURCE_SLOTS % current_resource.resource_type
        client = self._redis_maker()
        
        acquired = client.srem(weblab_resource_slots, current_resource.resource_instance) != 0
        return acquired

    @typecheck(Resource)
    def release_resource(self, current_resource):
        weblab_resource_slots = WEBLAB_RESOURCE_SLOTS % current_resource.resource_type
        client = self._redis_maker()

        client.sadd(weblab_resource_slots, current_resource.resource_instance)

    @typecheck(Resource)
    def release_resource_instance(self, resource):
        return self.release_resource(resource)

    @typecheck(ExperimentId)
    def get_resource_types_by_experiment_id(self, experiment_id):
        client = self._redis_maker()

        weblab_experiment_resources = WEBLAB_EXPERIMENT_RESOURCES % experiment_id.to_weblab_str()
        experiment_types = client.smembers(weblab_experiment_resources)
        if not client.exists(weblab_experiment_resources):
            raise CoordExc.ExperimentNotFoundError("Experiment not found: %s" % experiment_id)
        return set(experiment_types)

    @typecheck(ExperimentInstanceId)
    def get_resource_instance_by_experiment_instance_id(self, experiment_instance_id):
        experiment_id = experiment_instance_id.to_experiment_id()
        weblab_experiment_instance = WEBLAB_EXPERIMENT_INSTANCE % (experiment_id.to_weblab_str(), experiment_instance_id.inst_name)

        client = self._redis_maker()
        resource_instance = client.hget(weblab_experiment_instance, RESOURCE_INST)
        if resource_instance is None:
            raise CoordExc.ExperimentNotFoundError("Experiment not found: %s" % experiment_instance_id)

        return Resource.parse(resource_instance)

    def get_laboratory_coordaddress_by_experiment_instance_id(self, experiment_instance_id):
        experiment_id = experiment_instance_id.to_experiment_id()
        weblab_experiment_instance = WEBLAB_EXPERIMENT_INSTANCE % (experiment_id.to_weblab_str(), experiment_instance_id.inst_name)

        client = self._redis_maker()
        return client.hget(weblab_experiment_instance, LAB_COORD)

    @typecheck(Resource)
    def mark_resource_as_broken(self, resource):
        client = self._redis_maker()
        weblab_resource_working = WEBLAB_RESOURCE_WORKING % resource.resource_type
        return client.srem(weblab_resource_working, resource.resource_instance) != 0

    @typecheck(Resource)
    def mark_resource_as_fixed(self, resource):
        client = self._redis_maker()

        weblab_resource_working = WEBLAB_RESOURCE_WORKING % resource.resource_type
        return client.sadd(weblab_resource_working, resource.resource_instance) != 0

    @typecheck(ExperimentInstanceId)
    def remove_resource_instance_id(self, experiment_instance_id):
        client = self._redis_maker()

        experiment_id_str = experiment_instance_id.to_experiment_id().to_weblab_str()
        weblab_experiment_instances = WEBLAB_EXPERIMENT_INSTANCES % experiment_id_str
        weblab_experiment_instance  = WEBLAB_EXPERIMENT_INSTANCE % (experiment_id_str, experiment_instance_id.inst_name)

        resource_instance = client.hget(weblab_experiment_instance, RESOURCE_INST)
        if resource_instance is not None:
            # else it does not exist
            resource = Resource.parse(resource_instance)
            weblab_resource_experiment_instances = WEBLAB_RESOURCE_INSTANCE_EXPERIMENTS % (resource.resource_type, resource.resource_instance)
            client.srem(weblab_experiment_instances, experiment_instance_id.inst_name)
            client.delete(weblab_experiment_instance)
            client.srem(weblab_resource_experiment_instances, experiment_instance_id.to_weblab_str())

    @typecheck(Resource)
    def remove_resource_instance(self, resource):
        client = self._redis_maker()

        weblab_resource = WEBLAB_RESOURCE % resource.resource_type
        if client.srem(weblab_resource, resource.resource_instance):
            # else it did not exist
            weblab_resource_instance_experiments = WEBLAB_RESOURCE_INSTANCE_EXPERIMENTS % (resource.resource_type, resource.resource_instance)
            experiment_instances = client.smembers(weblab_resource_instance_experiments) or []
            client.delete(weblab_resource_instance_experiments)
            for experiment_instance in experiment_instances:
                experiment_instance_id = ExperimentInstanceId.parse(experiment_instance)
                self.remove_resource_instance_id(experiment_instance_id)

    @typecheck(basestring)
    def are_resource_instances_working(self, resource_type):
        client = self._redis_maker()
        resource_instances = client.smembers(WEBLAB_RESOURCE_WORKING % resource_type)
        return len(resource_instances) > 0

    @typecheck(Resource)
    def check_working(self, resource):
        if resource is None:
            return False
        client = self._redis_maker()
        resource_instances = client.smembers(WEBLAB_RESOURCE_WORKING % resource.resource_type)
        return resource.resource_instance in resource_instances

    def list_resources(self):
        client = self._redis_maker()
        return list(client.smembers(WEBLAB_RESOURCES))

    def list_resource_instances(self):
        client = self._redis_maker()
        resource_instances = []
        for resource_type in client.smembers(WEBLAB_RESOURCES):
            for resource_instance in client.smembers(WEBLAB_RESOURCE % resource_type):
                resource_instances.append(Resource(resource_type, resource_instance))

        return resource_instances
    
    @typecheck(basestring)
    def list_resource_instances_by_type(self, resource_type_name):
        client = self._redis_maker()
        return [ Resource(resource_type_name, resource_instance) for resource_instance in client.smembers(WEBLAB_RESOURCE % resource_type_name) ]

    def list_experiments(self):
        client = self._redis_maker()
        return [ ExperimentId.parse(exp_type) for exp_type in client.smembers(WEBLAB_EXPERIMENT_TYPES) ]

    @typecheck(ExperimentId)
    def list_experiment_instances_by_type(self, experiment_id):
        client = self._redis_maker()
        weblab_experiment_instances = WEBLAB_EXPERIMENT_INSTANCES % experiment_id.to_weblab_str()
        return [ 
            ExperimentInstanceId(inst, experiment_id.exp_name, experiment_id.cat_name)
            for inst in client.smembers(weblab_experiment_instances) ]

    @typecheck(basestring)
    def list_experiment_instance_ids_by_resource_type(self, resource_type):
        client = self._redis_maker()

        experiment_instance_ids = []

        instances = client.smembers(WEBLAB_RESOURCE % resource_type) or []
        for instance in instances:
            weblab_resource_instance_experiments = WEBLAB_RESOURCE_INSTANCE_EXPERIMENTS % (resource_type, instance)
            current_members = client.smembers(weblab_resource_instance_experiments) or []
            for member in current_members:
                experiment_instance_id = ExperimentInstanceId.parse(member)
                experiment_instance_ids.append(experiment_instance_id)

        return experiment_instance_ids

    @typecheck(Resource)
    def list_experiment_instance_ids_by_resource(self, resource):
        client = self._redis_maker()

        experiment_instance_ids = []

        weblab_resource_instance_experiments = WEBLAB_RESOURCE_INSTANCE_EXPERIMENTS % (resource.resource_type, resource.resource_instance)
        current_members = client.smembers(weblab_resource_instance_experiments) or []
        for member in current_members:
            experiment_instance_id = ExperimentInstanceId.parse(member)
            experiment_instance_ids.append(experiment_instance_id)

        return experiment_instance_ids

    def list_laboratories_addresses(self):
        client = self._redis_maker()

        laboratory_addresses = {
            # laboratory_coord_address : {
            #         experiment_instance_id : resource_instance
            # }
        }

        for experiment_type in client.smembers(WEBLAB_EXPERIMENT_TYPES):
            experiment_id = ExperimentId.parse(experiment_type)
            experiment_instance_names = client.smembers(WEBLAB_EXPERIMENT_INSTANCES % experiment_type)
            for experiment_instance_name in experiment_instance_names:
                experiment_instance_id = ExperimentInstanceId(experiment_instance_name, experiment_id.exp_name, experiment_id.cat_name)
                weblab_experiment_instance = WEBLAB_EXPERIMENT_INSTANCE % (experiment_type, experiment_instance_name)
                laboratory_address = client.hget(weblab_experiment_instance, LAB_COORD)
                resource_str       = client.hget(weblab_experiment_instance, RESOURCE_INST)
                resource           = Resource.parse(resource_str)
                current            = laboratory_addresses.get(laboratory_address, {})
                current[experiment_instance_id] = resource
                laboratory_addresses[laboratory_address] = current

        return laboratory_addresses

    @typecheck(basestring, ExperimentId, basestring)
    def associate_scheduler_to_reservation(self, reservation_id, experiment_id, resource_type_name):
        client = self._redis_maker()

        reservations_active_schedulers = WEBLAB_RESERVATIONS_ACTIVE_SCHEDULERS % reservation_id

        serialized = json.dumps({ EXPERIMENT_TYPE : experiment_id.to_weblab_str(), RESOURCE_TYPE : resource_type_name })
        client.sadd(reservations_active_schedulers, serialized)

    def dissociate_scheduler_from_reservation(self, reservation_id, experiment_id, resource_type_name):
        client = self._redis_maker()

        reservations_active_schedulers = WEBLAB_RESERVATIONS_ACTIVE_SCHEDULERS % reservation_id
        serialized = json.dumps({ EXPERIMENT_TYPE : experiment_id.to_weblab_str(), RESOURCE_TYPE : resource_type_name })

        return client.srem(reservations_active_schedulers, serialized) != 0

    def clean_associations_for_reservation(self, reservation_id, experiment_id):
        client = self._redis_maker()
        reservations_active_schedulers = WEBLAB_RESERVATIONS_ACTIVE_SCHEDULERS % reservation_id
        client.delete(reservations_active_schedulers)

    def retrieve_schedulers_per_reservation(self, reservation_id, experiment_id):
        client = self._redis_maker()

        reservations_active_schedulers = WEBLAB_RESERVATIONS_ACTIVE_SCHEDULERS % reservation_id
        
        associations = client.smembers(reservations_active_schedulers) or ()
        resource_type_names = []

        for member in associations:
            deserialized = json.loads(member)
            resource_type_names.append(deserialized[RESOURCE_TYPE])

        return resource_type_names

    def _clean(self):
        client = self._redis_maker()
        for element in client.smembers(WEBLAB_RESOURCES):
            for instance in client.smembers(WEBLAB_RESOURCE % element):
                client.delete(WEBLAB_RESOURCE_INSTANCE_EXPERIMENTS % (element, instance))
            client.delete(WEBLAB_RESOURCE % element)
            client.delete(WEBLAB_RESOURCE_EXPERIMENTS % element)
            client.delete(WEBLAB_RESOURCE_RESERVATIONS % element)
            client.delete(WEBLAB_RESOURCE_SLOTS % element)
            client.delete(WEBLAB_RESOURCE_WORKING % element)
        for element in client.keys(WEBLAB_RESOURCE_RESERVATIONS % '*'):
            client.delete(element)
        client.delete(WEBLAB_RESOURCES)

        for element in client.smembers(WEBLAB_EXPERIMENT_TYPES):
            client.delete(WEBLAB_EXPERIMENT_RESOURCES % element)
            for instance in client.smembers(WEBLAB_EXPERIMENT_INSTANCES % element):
                client.delete(WEBLAB_EXPERIMENT_INSTANCE % (element, instance))
            client.delete(WEBLAB_EXPERIMENT_INSTANCES % element)
        client.delete(WEBLAB_EXPERIMENT_TYPES)

