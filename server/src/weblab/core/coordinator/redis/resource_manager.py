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

from sqlalchemy.orm.exc import StaleDataError

from weblab.data.experiments import ExperimentId, ExperimentInstanceId
from weblab.core.coordinator.resource import Resource
import weblab.core.coordinator.exc as CoordExc

from voodoo.typechecker import typecheck

WEBLAB_RESOURCES = "weblab:resources"
WEBLAB_RESOURCE  = "weblab:resources:%s"


WEBLAB_EXPERIMENT_TYPES = "weblab:experiment_types"

WEBLAB_EXPERIMENT_INSTANCES = "weblab:experiment_types:%s:instances"
WEBLAB_EXPERIMENT_INSTANCE  = "weblab:experiment_types:%s:instances:%s"

WEBLAB_RESOURCE_EXPERIMENTS = "weblab:resources:%s:experiment_types"
WEBLAB_EXPERIMENT_RESOURCES = "weblab:experiment_types:%s:resource_types"

LAB_COORD     = "laboratory_coord_address"
RESOURCE_INST = "resource_instance"

class ResourcesManager(object):
    def __init__(self, client_creator):
        self._client_creator = client_creator

    @typecheck(Resource)
    def add_resource(self, resource):
        client = self._client_creator()
        client.sadd(WEBLAB_RESOURCES, resource.resource_type)
        client.sadd(WEBLAB_RESOURCE % resource.resource_type, resource.resource_instance)
        
    @typecheck(ExperimentId, basestring)
    def add_experiment_id(self, experiment_id, resource_type):
        client = self._client_creator()
        client.sadd(WEBLAB_RESOURCES, resource_type)
        client.sadd(WEBLAB_EXPERIMENT_TYPES, experiment_id.to_weblab_str())
    
    @typecheck(basestring, ExperimentInstanceId, Resource)
    def add_experiment_instance_id(self, laboratory_coord_address, experiment_instance_id, resource):
        self.add_resource(resource)

        experiment_id     = experiment_instance_id.to_experiment_id()
        experiment_id_str = experiment_id.to_weblab_str()

        self.add_experiment_id(experiment_id, resource.resource_type)

        client = self._client_creator()
        client.sadd(WEBLAB_EXPERIMENT_INSTANCES % experiment_id_str, experiment_instance_id.inst_name)

        weblab_experiment_instance = WEBLAB_EXPERIMENT_INSTANCE % (experiment_id_str, experiment_instance_id.inst_name)

        weblab_resource_experiments = WEBLAB_RESOURCE_EXPERIMENTS % resource.resource_type
        client.sadd(weblab_resource_experiments, experiment_id_str)
        
        weblab_experiment_resources = WEBLAB_EXPERIMENT_RESOURCES % experiment_id_str
        client.sadd(weblab_experiment_resources, resource.resource_type)

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

    def acquire_resource(self, session, current_resource_slot):
        # TODO: XXX: this makes no sense in redis

        slot_reservation = SchedulingSchemaIndependentSlotReservation(current_resource_slot)
        session.add(slot_reservation)
        return slot_reservation

    def release_resource(self, session, slot_reservation):
        session.delete(slot_reservation)

    def release_resource_instance(self, session, resource):
        # TODO: test me
        resource_instance = self._get_resource_instance(session, resource)
        slot = resource_instance.slot
        if slot is not None:
            slot_reservation = slot.slot_reservation
            if slot_reservation is not None:
                self.release_resource(session, slot_reservation)

    @typecheck(ExperimentId)
    def get_resource_types_by_experiment_id(self, experiment_id):
        client = self._client_creator()

        weblab_experiment_resources = WEBLAB_EXPERIMENT_RESOURCES % experiment_id.to_weblab_str()
        experiment_types = client.smembers(weblab_experiment_resources)
        if not client.exists(weblab_experiment_resources):
            raise CoordExc.ExperimentNotFoundError("Experiment not found: %s" % experiment_id)
        return set(experiment_types)

    def get_resource_instance_by_experiment_instance_id(self, experiment_instance_id):
        experiment_id = experiment_instance_id.to_experiment_id()
        weblab_experiment_instance = WEBLAB_EXPERIMENT_INSTANCE % (experiment_id.to_weblab_str(), experiment_instance_id.inst_name)

        client = self._client_creator()
        resource_instance = client.hget(weblab_experiment_instance, RESOURCE_INST)
        if resource_instance is None:
                raise CoordExc.ExperimentNotFoundError("Experiment not found: %s" % experiment_instance_id)

        return Resource.parse(resource_instance)

    def _get_resource_instance(self, session, resource):
        db_resource_type = session.query(ResourceType).filter_by(name = resource.resource_type).one()
        db_resource_instance = session.query(ResourceInstance).filter_by(name = resource.resource_instance, resource_type = db_resource_type).one()
        return db_resource_instance

    def mark_resource_as_broken(self, session, resource):
        db_resource_instance = self._get_resource_instance(session, resource)

        db_slot = db_resource_instance.slot
        if not db_slot is None:
            session.delete(db_slot)
            return True
        return False

    def mark_resource_as_fixed(self, resource):
        session = self._session_maker()
        try:
            db_resource_instance = self._get_resource_instance(session, resource)
    
            db_slot = db_resource_instance.slot
            if db_slot is None:
                db_slot = CurrentResourceSlot(db_resource_instance)
                session.add(db_slot)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def remove_resource_instance_id(self, session, experiment_instance_id):
        exp_type = session.query(ExperimentType).filter_by(cat_name = experiment_instance_id.cat_name).first()
        if exp_type is None:
            return # The experiment is not there anyway

        exp_inst = session.query(ExperimentInstance).filter_by(experiment_instance_id = experiment_instance_id.inst_name, experiment_type = exp_type).first()
        if exp_inst is None:
            return # The experiment is not there anyway

        session.delete(exp_inst) # Delete it if it's there

    def remove_resource_instance(self, session, resource):
        resource_type = session.query(ResourceType).filter_by(name = resource.resource_type).first()
        if resource_type is None:
            return # The resource is not there anyway

        resource_instance = session.query(ResourceInstance).filter_by(name = resource.resource_instance, resource_type = resource_type).first()
        if resource_instance is None:
            return # The resource is no there anyway

        for experiment_instance in resource_instance.experiment_instances:
            experiment_instance_id = experiment_instance.to_experiment_instance_id()
            self.remove_resource_instance_id(session, experiment_instance_id)

        session.delete(resource_instance)

    def list_resources(self):
        client = self._client_creator()
        return list(client.smembers(WEBLAB_RESOURCES))

    def list_resource_instances(self):
        client = self._client_creator()
        resource_instances = []
        for resource_type in client.smembers(WEBLAB_RESOURCES):
            for resource_instance in client.smembers(WEBLAB_RESOURCE % resource_type):
                resource_instances.append(Resource(resource_type, resource_instance))

        return resource_instances

    def list_experiments(self):
        client = self._client_creator()
        return [ ExperimentId.parse(exp_type) for exp_type in client.smembers(WEBLAB_EXPERIMENT_TYPES) ]

    @typecheck(ExperimentId)
    def list_experiment_instances_by_type(self, experiment_id):
        client = self._client_creator()
        weblab_experiment_instances = WEBLAB_EXPERIMENT_INSTANCES % experiment_id.to_weblab_str()
        return [ 
            ExperimentInstanceId(inst, experiment_id.exp_name, experiment_id.cat_name)
            for inst in client.smembers(weblab_experiment_instances) ]

    @typecheck(basestring)
    def list_experiment_instance_ids_by_resource(self, resource_type):
        client = self._client_creator()

        weblab_resource_experiments = WEBLAB_RESOURCE_EXPERIMENTS % resource_type
        retrieved_resource_experiments = client.smembers(weblab_resource_experiments) or []
        return [
                    ExperimentId.parse(experiment_id_str) 
                    for experiment_id_str in retrieved_resource_experiments]


    def list_laboratories_addresses(self):
        session = self._session_maker()

        try:
            experiment_instances = session.query(ExperimentInstance).all()

            laboratories_addresses = {}

            for experiment_instance in experiment_instances:
                current  = laboratories_addresses.get(experiment_instance.laboratory_coord_address, {})
                current[experiment_instance.to_experiment_instance_id()] = experiment_instance.resource_instance.to_resource()
                laboratories_addresses[experiment_instance.laboratory_coord_address] = current
        finally:
            session.close()

        return laboratories_addresses

    def associate_scheduler_to_reservation(self, reservation_id, experiment_id, resource_type_name):
        session = self._session_maker()
        try:
            db_resource_type = session.query(ResourceType).filter_by(name = resource_type_name).first()
            db_experiment_type = session.query(ExperimentType).filter_by(cat_name = experiment_id.cat_name, exp_name = experiment_id.exp_name).first()

            association = ActiveReservationSchedulerAssociation(reservation_id, db_experiment_type, db_resource_type)
            session.add(association)
            session.commit()
        finally:
            session.close()

    def dissociate_scheduler_from_reservation(self, reservation_id, experiment_id, resource_type_name):
        session = self._session_maker()
        try:
            db_resource_type = session.query(ResourceType).filter_by(name = resource_type_name).first()
            db_experiment_type = session.query(ExperimentType).filter_by(cat_name = experiment_id.cat_name, exp_name = experiment_id.exp_name).first()

            association = session.query(ActiveReservationSchedulerAssociation).filter_by(reservation_id = reservation_id, experiment_type = db_experiment_type, resource_type = db_resource_type).first()
            if association is not None:
                session.delete(association)
                try:
                    session.commit()
                except StaleDataError:
                    pass
        finally:
            session.close()

    def clean_associations_for_reservation(self, reservation_id, experiment_id):
        session = self._session_maker()
        try:
            db_experiment_type = session.query(ExperimentType).filter_by(cat_name = experiment_id.cat_name, exp_name = experiment_id.exp_name).first()

            associations = session.query(ActiveReservationSchedulerAssociation).filter_by(reservation_id = reservation_id, experiment_type = db_experiment_type).all()
            found = False
            for association in associations:
                session.delete(association)
                found = True

            if found:
                session.commit()
        finally:
            session.close()

    def retrieve_schedulers_per_reservation(self, reservation_id, experiment_id):
        session = self._session_maker()
        try:
            db_experiment_type = session.query(ExperimentType).filter_by(cat_name = experiment_id.cat_name, exp_name = experiment_id.exp_name).first()

            associations = session.query(ActiveReservationSchedulerAssociation).filter_by(reservation_id = reservation_id, experiment_type = db_experiment_type).all()
            resource_type_names = []
            for association in associations:
                resource_type_names.append(association.resource_type.name)

            return resource_type_names
        finally:
            session.close()

    def _clean(self):
        client = self._client_creator()
        for element in client.smembers(WEBLAB_RESOURCES):
            client.delete(WEBLAB_RESOURCE % element)
        client.delete(WEBLAB_RESOURCES)
#         session = self._session_maker()
#         try:
#             for association in session.query(ActiveReservationSchedulerAssociation).all():
#                 session.delete(association)
#             for slot_reservation in session.query(SchedulingSchemaIndependentSlotReservation).all():
#                 session.delete(slot_reservation)
#             for resource_slot in session.query(CurrentResourceSlot).all():
#                 session.delete(resource_slot)
#             for experiment_instance in session.query(ExperimentInstance).all():
#                 session.delete(experiment_instance)
#             for experiment_type in session.query(ExperimentType).all():
#                 session.delete(experiment_type)
#             for resource_instance in session.query(ResourceInstance).all():
#                 session.delete(resource_instance)
#             for resource_type in session.query(ResourceType).all():
#                 session.delete(resource_type)
#             session.commit()
#         finally:
#             session.close()

