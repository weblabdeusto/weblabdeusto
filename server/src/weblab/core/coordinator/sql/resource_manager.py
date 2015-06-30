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

from sqlalchemy.orm.exc import StaleDataError

from weblab.core.coordinator.sql.model import ResourceType, ResourceInstance, CurrentResourceSlot, SchedulingSchemaIndependentSlotReservation, ExperimentInstance, ExperimentType, ActiveReservationSchedulerAssociation
import weblab.core.coordinator.exc as CoordExc

class ResourcesManager(object):
    def __init__(self, session_maker):
        self._session_maker = session_maker

    def add_resource(self, session, resource):
        db_resource_type = session.query(ResourceType).filter_by(name = resource.resource_type).first()
        if db_resource_type is None:
            db_resource_type = ResourceType(resource.resource_type)
            session.add(db_resource_type)

        db_resource_instance = session.query(ResourceInstance).filter_by(name = resource.resource_instance, resource_type = db_resource_type).first()
        if db_resource_instance is None:
            db_resource_instance = ResourceInstance(db_resource_type, resource.resource_instance)
            session.add(db_resource_instance)

        db_slot = db_resource_instance.slot
        if db_slot is None:
            db_slot = CurrentResourceSlot(db_resource_instance)
            session.add(db_slot)

    def add_experiment_id(self, session, experiment_id, resource_type):
        db_resource_type = session.query(ResourceType).filter_by(name = resource_type).first()
        if db_resource_type is None:
            db_resource_type = ResourceType(resource_type)
            session.add(db_resource_type)

        db_experiment_type = session.query(ExperimentType).filter_by(cat_name = experiment_id.cat_name, exp_name = experiment_id.exp_name).first()
        if db_experiment_type is None:
            db_experiment_type = ExperimentType(experiment_id.exp_name, experiment_id.cat_name)
            session.add(db_experiment_type)

        if not db_resource_type in db_experiment_type.resource_types:
            db_experiment_type.resource_types.append(db_resource_type)

        return db_resource_type, db_experiment_type

    def add_experiment_instance_id(self, laboratory_coord_address, experiment_instance_id, resource):
        session = self._session_maker()
        try:
            self.add_resource(session, resource)

            db_resource_type, db_experiment_type = self.add_experiment_id(session, experiment_instance_id.to_experiment_id(), resource.resource_type)

            db_resource_instance = session.query(ResourceInstance).filter_by(name = resource.resource_instance, resource_type = db_resource_type).first()

            db_experiment_instance = session.query(ExperimentInstance).filter_by(experiment_instance_id = experiment_instance_id.inst_name, experiment_type = db_experiment_type).first()
            if db_experiment_instance is None:
                db_experiment_instance = ExperimentInstance(db_experiment_type, laboratory_coord_address, experiment_instance_id.inst_name)
                session.add(db_experiment_instance)
            else:
                retrieved_laboratory_coord_address = db_experiment_instance.laboratory_coord_address
                if retrieved_laboratory_coord_address != laboratory_coord_address:
                    raise CoordExc.InvalidExperimentConfigError("Attempt to register the experiment %s in the laboratory %s; this experiment is already registered in the laboratory %s" % (experiment_instance_id, laboratory_coord_address, retrieved_laboratory_coord_address))
                if db_experiment_instance.resource_instance != db_resource_instance:
                    raise CoordExc.InvalidExperimentConfigError("Attempt to register the experiment %s with resource %s when it was already bound to resource %s" % (experiment_instance_id, resource, db_experiment_instance.resource_instance.to_resource()))

            db_experiment_instance.resource_instance = db_resource_instance
            session.commit()
        finally:
            session.close()

    def acquire_resource(self, session, current_resource_slot):
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

    def get_resource_types_by_experiment_id(self, experiment_id):
        session = self._session_maker()
        try:
            experiment_type = session.query(ExperimentType).filter_by(cat_name = experiment_id.cat_name, exp_name = experiment_id.exp_name).first()
            if experiment_type is None:
                raise CoordExc.ExperimentNotFoundError("Experiment not found: %s" % experiment_id)

            resource_types = set()
            for resource_type in experiment_type.resource_types:
                resource_types.add(resource_type.name)
            return resource_types
        finally:
            session.close()

    def get_resource_instance_by_experiment_instance_id(self, experiment_instance_id):
        session = self._session_maker()
        try:
            experiment_type = session.query(ExperimentType).filter_by(cat_name = experiment_instance_id.cat_name, exp_name = experiment_instance_id.exp_name).first()
            if experiment_type is None:
                raise CoordExc.ExperimentNotFoundError("Experiment not found: %s" % experiment_instance_id)

            experiment_instance = session.query(ExperimentInstance).filter_by(experiment_type = experiment_type, experiment_instance_id = experiment_instance_id.inst_name).first()
            if experiment_instance is None:
                raise CoordExc.ExperimentNotFoundError("Experiment not found: %s" % experiment_instance_id)
            return experiment_instance.resource_instance.to_resource()
        finally:
            session.close()

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
        session = self._session_maker()
        try:
            resource_types = session.query(ResourceType).order_by(ResourceType.id).all()
            resource_type_names = []
            for resource_type in resource_types:
                resource_type_names.append(resource_type.name)
        finally:
            session.close()

        return resource_type_names

    def list_experiments(self):
        session = self._session_maker()

        try:
            experiment_types = session.query(ExperimentType).order_by(ExperimentType.id).all()

            experiment_ids = []

            for experiment_type in experiment_types:
                experiment_ids.append(experiment_type.to_experiment_id())
        finally:
            session.close()

        return experiment_ids

    def list_experiment_instance_ids_by_resource(self, resource):
        session = self._session_maker()

        try:
            db_resource_instance = self._get_resource_instance(session, resource)
            experiment_instance_ids = []
            for experiment_instance in db_resource_instance.experiment_instances:
                experiment_instance_id = experiment_instance.to_experiment_instance_id()
                experiment_instance_ids.append(experiment_instance_id)
        finally:
            session.close()

        return experiment_instance_ids


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
        session = self._session_maker()
        try:
            for association in session.query(ActiveReservationSchedulerAssociation).all():
                session.delete(association)
            for slot_reservation in session.query(SchedulingSchemaIndependentSlotReservation).all():
                session.delete(slot_reservation)
            for resource_slot in session.query(CurrentResourceSlot).all():
                session.delete(resource_slot)
            for experiment_instance in session.query(ExperimentInstance).all():
                session.delete(experiment_instance)
            for experiment_type in session.query(ExperimentType).all():
                session.delete(experiment_type)
            for resource_instance in session.query(ResourceInstance).all():
                session.delete(resource_instance)
            for resource_type in session.query(ResourceType).all():
                session.delete(resource_type)
            session.commit()
        finally:
            session.close()


