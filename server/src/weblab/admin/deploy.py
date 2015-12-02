#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 onwards University of Deusto
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

import os
import sys
import datetime
import traceback
import random
import hashlib

import six
from sqlalchemy.orm import sessionmaker

from weblab.db.upgrade import DbRegularUpgrader, DbSchedulingUpgrader
from weblab.admin.util import password2sha
import weblab.db.model as model
import weblab.permissions as permissions



def _add_params(session, experiment, params = None):
    if params is None:
        experiment_config = CONFIG_JS[experiment.name + '@' + experiment.category.name]
    else:
        experiment_config = params

    for key, value in experiment_config.iteritems():
        if key in ("experiment.name", "experiment.category"):
            continue

        if isinstance(value, bool):
            key_type = 'bool'
        elif isinstance(value, int):
            key_type = 'integer'
        elif isinstance(value, float):
            key_type = 'floating'
        else:
            key_type = 'string'

        param = model.DbExperimentClientParameter(experiment, key, key_type, unicode(value))
        session.add(param)

    session.commit()

#
# Please keep the alphabetical order
#
CONFIG_JS = {
    "aquarium@Aquatic experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#aquarium",
        "experiment.picture": "/img/experiments/aquarium.png",
        "builtin": True
    },
    "aquariumjs@Aquatic experiments": {
        "height": 1000,
        "width": 1024,
        "html.file": "jslabs/aquarium/aquarium.html",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#aquarium",
        "experiment.info.description": "description",
        "experiment.picture": "/img/experiments/aquarium.png",
        "builtin": True
    },
    "archimedes@Aquatic experiments": {
        "html.file": "jslabs/archimedes/archimedes.html",
        "cssHeight": "1000",
        "cssWidth": "1024",
        "experiment.picture": "/img/experiments/aquarium.png",
        "builtin": True
    },
    "binary@Games": {
        "experiment.picture": "/img/experiments/binary.jpg"
    },
    "blink-led@LabVIEW experiments": {
        "experiment.picture": "/img/experiments/labview.jpg"
    },
    "control-app@Control experiments": {
        "experiment.picture": "/img/experiments/bulb.png"
    },
    "dummy1@Dummy experiments": {},
    "dummy2@Dummy experiments": {},
    "dummy3@Dummy experiments": {},
    "dummy3_with_other_name@Dummy experiments": {},
    "dummy4@Dummy experiments": {},
    "dummy@Dummy experiments": {},
    "elevator@FPGA experiments": {
        "cssHeight": "1000",
        "cssWidth": "1024",
        "html.file": "jslabs/elevator/dist/index.html",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#elevator",
        "experiment.info.description": "Experiment with an elevator",
        "experiment.picture": "/img/experiments/elevator.png",
        "builtin": True
    },
    "external-robot-movement@Robot experiments": {
        "html": "This is an experiment which we know that it is only in external systems. Therefore, unless we want to use the initialization API, we don't need to have the client installed in the consumer system. We can just use a blank client and whenever the experiment is reserved, we'll use the remote client.",
        "experiment.picture": "/img/experiments/robot.jpg"
    },
    "Fisica-1-PXI@Visir experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
        "experiment.picture": "/img/experiments/visir.jpg"
    },
    "Fisica-1@Visir experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
        "experiment.picture": "/img/experiments/visir.jpg"
    },
    "Fisica-2-PXI@Visir experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
        "experiment.picture": "/img/experiments/visir.jpg"
    },
    "Fisica-2@Visir experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
        "experiment.picture": "/img/experiments/visir.jpg"
    },
    "Fisica-3-PXI@Visir experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
        "experiment.picture": "/img/experiments/visir.jpg"
    },
    "Fisica-3@Visir experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
        "experiment.picture": "/img/experiments/visir.jpg"
    },
    "flashdummy@Dummy experiments": {
        "swf.file": "WeblabFlashSample.swf",
        "experiment.info.description": "description",
        "height": 350,
        "message": "Note: This is not a real experiment, it's just a demo so as to show that WebLab-Deusto can integrate different web technologies (such as Adobe Flash in this experiment). This demostrates that developing experiments in WebLab-Deusto is really flexible.",
        "flash.timeout": 20,
        "width": 500,
        "experiment.info.link": "http://code.google.com/p/weblabdeusto/wiki/Latest_Exp_Flash_Dummy",
        "experiment.picture": "/img/experiments/flash.jpg",
        "page.footer": ""
    },
    "fpga-board-bit@LabVIEW experiments": {
        "experiment.picture": "/img/experiments/labview.jpg"
    },
    "fpga-board-config@LabVIEW experiments": {
        "experiment.picture": "/img/experiments/labview.jpg"
    },
    "fpga-board-experiment@LabVIEW experiments": {
        "send.file": True,
        "experiment.picture": "/img/experiments/labview.jpg"
    },
    "http@HTTP experiments": {},
    "hwboard-fpga@FPGA experiments": {
        "html.file": "jslabs/hwboard/dist/index.html",
        "provide.file.upload": True,
        "height": "600",
        "width": "800",
        "experiment.picture": "/img/experiments/xilinx.jpg",
        "builtin": True
    },
    "hwboard-fpga-watertank@FPGA experiments": {
        "html.file": "jslabs/hwboard/dist/index.html",
        "provide.file.upload": False,
        "experiment.picture": "/img/experiments/xilinx.jpg",
        "virtualmodel": "watertank",
        "builtin": True
    },
    "incubator@Farm experiments": {
        "html": "This lab is disabled at this moment. Go to <a target=\"_blank\" href=\"http://130.206.138.18/lastexp/\">the original site</a> to see the archived results.",
        "experiment.reserve.button.shown": False,
        "experiment.picture": "/img/experiments/incubator.jpg"
    },
    "new_incubator@Farm experiments": {
        "cssWidth": "1000",
        "cssHeight": "700",
        "provide.file.upload": False,
        "experiment.picture": "/img/experiments/incubator.jpg",
        "html.file": "jslabs/incubator/incubator.html"
    },
    "javadummy@Dummy experiments": {
        "height": 350,
        "width": 500,
        "code": "es.deusto.weblab.client.experiment.plugins.es.deusto.weblab.javadummy.JavaDummyApplet",
        "experiment.info.description": "description",
        "experiment.info.link": "http://code.google.com/p/weblabdeusto/wiki/Latest_Exp_Java_Dummy",
        "message": "Note: This is not a real experiment, it's just a demo so as to show that WebLab-Deusto can integrate different web technologies (such as Java Applets in this experiment). This demostrates that developing experiments in WebLab-Deusto is really flexible.",
        "jar.file": "WeblabJavaSample.jar",
        "experiment.picture": "/img/experiments/java.jpg"
    },
    "jsdummy@Dummy experiments": {
        "html.file": "jstest.html",
        "provide.file.upload": True,
        "height": 350,
        "width": 500,
        "experiment.picture": "/img/experiments/java.jpg"
    },
    "jsfpga@FPGA experiments": {
        "html.file": "jsxilinx/watertank/watertank.html",
        "provide.file.upload": True,
        "height": "600",
        "width": "800",
        "experiment.picture": "/img/experiments/xilinx.jpg"
    },
    "logic@Games": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#ud-logic",
        "experiment.picture": "/img/experiments/logic.jpg"
    },
    "lxi_visir@Visir experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
        "experiment.picture": "/img/experiments/visir.jpg"
    },
    "microelectronics@iLab experiments": {
        "code": "weblab.client.graphicalUI.GraphicalApplet",
        "experiment.reserve.button.shown": False,
        "service_broker": "http://www.weblab.deusto.es/weblab/web/ilab/",
        "archive": "http://weblab2.mit.edu/client/v7.0b5/signed_Weblab-client.jar",
        "lab_server_id": "microelectronics",
        "experiment.picture": "/img/experiments/MIT.jpg"
    },
    "prototyping-board-01@LabVIEW experiments": {
        "experiment.picture": "/img/experiments/labview.jpg"
    },
    "robot-maze@Robot experiments": {
        "experiment.picture": "/img/experiments/robot.jpg"
    },
    "robot-movement@Robot experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#robot",
        "experiment.picture": "/img/experiments/robot.jpg"
    },
    "robot-proglist@Robot experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#robot",
        "experiment.picture": "/img/experiments/robot.jpg"
    },
    "robot-standard@Robot experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#robot",
        "experiment.picture": "/img/experiments/robot.jpg"
    },
    "robotarm@Robot experiments": {
        "experiment.info.description": "description",
        "experiment.picture": "/img/experiments/robot.jpg"
    },
    "romie@Robot experiments": {
        "cssWidth": "1200",
        "cssHeight": "700",
        "provide.file.upload": False,
        "experiment.picture": "/img/experiments/romie.png",
        "html.file": "jslabs/romie/romie.html",
        "builtin": True
    },
    "romie_labpsico@Robot experiments": {
        "cssWidth": "1200",
        "cssHeight": "700",
        "provide.file.upload": False,
        "experiment.picture": "/img/experiments/romie.png",
        "html.file": "jslabs/romie/romie.html",
        "builtin": True
    },
    "romie_demo@Robot experiments": {
        "cssWidth": "1200",
        "cssHeight": "700",
        "provide.file.upload": False,
        "experiment.picture": "/img/experiments/romie.png",
        "html.file": "jslabs/romie/romie.html",
        "builtin": True
    },
    "romie_blockly@Robot experiments": {
        "cssWidth": "1200",
        "cssHeight": "540",
        "provide.file.upload": False,
        "experiment.picture": "/img/experiments/romie.png",
        "html.file": "jslabs/romieblocks/index.html",
        "builtin": True
    },
    "submarine@Aquatic experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#aquarium",
        "experiment.picture": "/img/experiments/submarine.png"
    },
    "submarine@Submarine experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#aquarium",
        "experiment.picture": "/img/experiments/submarine.png"
    },
    "submarinejs@Aquatic experiments": {
        "cssHeight": "1000",
        "cssWidth": "1024",
        "html.file": "jslabs/submarine/submarine.html",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#aquarium",
        "experiment.info.description": "description",
        "experiment.picture": "/img/experiments/submarine.png"
    },
    "testone@LabVIEW experiments": {
        "experiment.picture": "/img/experiments/labview.jpg"
    },
    "ud-binary@PLD experiments": {
        "experiment.picture": "/img/experiments/binary.jpg"
    },
    "ud-demo-fpga@FPGA experiments": {
        "experiment.info.description": "description",
        "is.demo": True,
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#fpga",
        "experiment.picture": "/img/experiments/xilinx.jpg"
    },
    "ud-demo-pld@PLD experiments": {
        "experiment.info.description": "description",
        "is.demo": True,
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#cpld",
        "experiment.picture": "/img/experiments/xilinx.jpg"
    },
    "ud-demo-xilinx@Xilinx experiments": {
        "experiment.info.description": "description",
        "is.demo": True,
        "experiment.info.link": "http://code.google.com/p/weblabdeusto/wiki/Latest_Exp_Demo_Xilinx",
        "is.multiresource.demo": True,
        "experiment.picture": "/img/experiments/xilinx.jpg"
    },
    "ud-dummy-batch@Dummy experiments": {},
    "ud-dummy@Dummy experiments": {
        "html.file": "nativelabs/dummy.html",
        "builtin" : True,
        "message": "(This message comes from the admin panel)"
    },
    "ud-fpga@FPGA experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#fpga",
        "experiment.picture": "/img/experiments/xilinx.jpg"
    },
    "ud-gpib1@GPIB experiments": {},
    "ud-gpib2@GPIB experiments": {},
    "ud-gpib@GPIB experiments": {},
    "ud-linux-vm@VM experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#virtual-machine-lab",
        "experiment.picture": "/img/experiments/virtualbox.jpg"
    },
    "ud-logic@Dummy experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#ud-logic",
        "experiment.picture": "/img/experiments/logic.jpg"
    },
    "ud-logic@PIC experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#ud-logic",
        "experiment.picture": "/img/experiments/logic.jpg"
    },
    "ud-pic18@PIC experiments": {
        "experiment.picture": "/img/experiments/microchip.jpg"
    },
    "ud-pld-1@PLD experiments": {
        "experiment.picture": "/img/experiments/xilinx.jpg"
    },
    "ud-pld-2@PLD experiments": {
        "experiment.picture": "/img/experiments/xilinx.jpg"
    },
    "ud-pld@PLD experiments": {
        "experiment.picture": "/img/experiments/xilinx.jpg"
    },
    "ud-test-pic18-1@PIC experiments": {
        "is.demo": True,
        "experiment.picture": "/img/experiments/microchip.jpg"
    },
    "ud-test-pic18-2@PIC experiments": {
        "is.demo": True,
        "experiment.picture": "/img/experiments/microchip.jpg"
    },
    "ud-test-pic18-3@PIC experiments": {
        "is.demo": True,
        "experiment.picture": "/img/experiments/microchip.jpg"
    },
    "ud-test-pld1@PLD experiments": {
        "is.demo": True,
        "experiment.picture": "/img/experiments/xilinx.jpg"
    },
    "ud-test-pld2@PLD experiments": {
        "is.demo": True,
        "experiment.picture": "/img/experiments/xilinx.jpg"
    },
    "ud-win-vm@VM experiments": {
        "experiment.picture": "/img/experiments/virtualbox.jpg"
    },
    "unr-physics@Physics experiments": {
        "experiment.picture": "/img/experiments/unr.jpg",
        "builtin": True,
        "html.file": "jslabs/unr_physics.html"
    },
    "visir-fed-balance-multiple@Visir experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
        "experiment.picture": "/img/experiments/visir.jpg"
    },
    "visir-fed-balance@Visir experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
        "experiment.picture": "/img/experiments/visir.jpg"
    },
    "visir-html5@Visir experiments": {
        "html.file": "jslabs/visir-html5/visir.html",
        "builtin": True,
        "provide.file.upload": False,
        "cssHeight": "520",
        "cssWidth": "805",
        "experiment.picture": "/img/experiments/visir.jpg"
    },
    "visir-lesson2@Visir experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
        "experiment.picture": "/img/experiments/visir.jpg"
    },
    "visir-student@Visir experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
        "experiment.picture": "/img/experiments/visir.jpg"
    },
    "visir-uned@Visir experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
        "experiment.picture": "/img/experiments/visir.jpg"
    },
    "visir@Visir experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
        "experiment.picture": "/img/experiments/visir.jpg"
    },
    "visirtest@Dummy experiments": {
        "experiment.info.description": "description",
        "experiment.info.link": "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
        "experiment.picture": "/img/experiments/visir.jpg"
    },
    "vm-win@Dummy experiments": {
        "experiment.picture": "/img/experiments/virtualbox.jpg"
    },
    "vm@Dummy experiments": {
        "experiment.picture": "/img/experiments/virtualbox.jpg"
    },
    "vm@VM experiments": {
        "experiment.picture": "/img/experiments/virtualbox.jpg"
    }
}

def insert_required_initial_data(engine):
    session = sessionmaker(bind=engine)
    session._model_changes = {}
    session = session()

    # Roles
    federated = model.DbRole("federated")
    session.add(federated)

    administrator = model.DbRole("administrator")
    session.add(administrator)

    instructor = model.DbRole("instructor")
    session.add(instructor)

    student = model.DbRole("student")
    session.add(student)

    db = model.DbAuthType("DB")
    session.add(db)
    ldap = model.DbAuthType("LDAP")
    session.add(ldap)
    iptrusted = model.DbAuthType("TRUSTED-IP-ADDRESSES")
    session.add(iptrusted)
    facebook = model.DbAuthType("FACEBOOK")
    session.add(facebook)
    openid = model.DbAuthType("OPENID")
    session.add(openid)

    weblab_db = model.DbAuth(db, "WebLab DB", 1)
    session.add(weblab_db)
    session.commit()

    weblab_openid = model.DbAuth(openid, "OPENID", 7)
    session.add(weblab_openid)
    session.commit()

    federated_access_forward = model.DbRolePermission(
        federated,
        permissions.ACCESS_FORWARD,
        "federated_role::access_forward",
        datetime.datetime.utcnow(),
        "Access to forward external accesses to all users with role 'federated'"
    )
    session.add(federated_access_forward)

    session.commit()

    administrator_admin_panel_access = model.DbRolePermission(
        administrator,
        permissions.ADMIN_PANEL_ACCESS,
        "administrator_role::admin_panel_access",
        datetime.datetime.utcnow(),
        "Access to the admin panel for administrator role with full_privileges"
    )
    session.add(administrator_admin_panel_access)
    administrator_admin_panel_access_p1 = model.DbRolePermissionParameter(administrator_admin_panel_access, permissions.FULL_PRIVILEGES, True)
    session.add(administrator_admin_panel_access_p1)

    administrator_access_all_labs = model.DbRolePermission(
        administrator,
        permissions.ACCESS_ALL_LABS,
        "administrator_role::access_all_labs",
        datetime.datetime.utcnow(),
        "Access all the laboratories"
    )
    session.add(administrator_access_all_labs)

    upgrader = DbRegularUpgrader(str(engine.url))
    session.execute(
        model.Base.metadata.tables['alembic_version'].insert().values(version_num = upgrader.head)
    )
    session.commit()

def insert_required_initial_coord_data(engine):
    session = sessionmaker(bind=engine)
    session = session()

    upgrader = DbSchedulingUpgrader(str(engine.url))
    session.execute(
        model.Base.metadata.tables['alembic_version'].insert().values(version_num = upgrader.head)
    )
    session.commit()

#####################################################################
#
# Populating tests database
#

def _create_user(session, login, role, full_name, email, password = 'password', invalid_password = None, other_auths = None):
    user = model.DbUser(login, full_name, email, None, role)
    session.add(user)
    weblab_db = session.query(model.DbAuth).filter_by(name = "WebLab DB").one()
    if not invalid_password:
        session.add(model.DbUserAuth(user, weblab_db, password2sha(password, 'aaaa')))
    else:
        session.add(model.DbUserAuth(user, weblab_db, invalid_password))
    for (auth_type, value) in (other_auths or ()):
        session.add(model.DbUserAuth(user, auth_type, value))
    return user

def _create_users(session, users_data):
    all_users = {}
    for login, data in six.iteritems(users_data):
        all_users[login] = _create_user(session, login, *data)
    return all_users

def _create_group(session, users_data, group_name, logins, parent):
    group = model.DbGroup(group_name, parent)
    for login in logins:
        group.users.append(users_data[login])
    session.add(group)
    return group

def _create_groups(session, users_data, groups_data):
    all_groups = {}
    for (group_name, parent_name), logins in six.iteritems(groups_data):
        if parent_name is None:
            all_groups[group_name] = _create_group(session, users_data, group_name, logins, None)

    for (group_name, parent_name), logins in six.iteritems(groups_data):
        if parent_name is not None:
            parent = all_groups[parent_name]
            all_groups[group_name] = _create_group(session, users_data, group_name, logins, parent)

    return all_groups

def _create_experiment(session, exp_name, cat_name, client):
    start_date = datetime.datetime.utcnow()
    end_date = start_date.replace(year=start_date.year+12) # So leap years are not a problem

    category = session.query(model.DbExperimentCategory).filter_by(name = cat_name).first()
    if category is None:
        category = model.DbExperimentCategory(cat_name)
        session.add(category)

    experiment = model.DbExperiment(exp_name, category, start_date, end_date, client)
    session.add(experiment)
    _add_params(session, experiment)
    return experiment

def _create_experiments(session, experiment_data):
    all_experiments = {}
    for (exp_name, cat_name), client in six.iteritems(experiment_data):
        all_experiments[exp_name, cat_name] = _create_experiment(session, exp_name, cat_name, client)
    return all_experiments

def _grant_permission_to_group(session, groups_data, experiments_data, group_name, exp_name, cat_name, time):
    if (exp_name, cat_name) not in experiments_data:
        raise Exception("Error: %s@%s not previously registered" % (exp_name, cat_name))

    db_group = groups_data[group_name]

    gp_allowed = model.DbGroupPermission(
        db_group,
        permissions.EXPERIMENT_ALLOWED,
        "%s::%s" % (group_name, exp_name),
        datetime.datetime.utcnow(),
        "Permission for group %s to use %s" % (group_name, exp_name)
    )
    session.add(gp_allowed)
    gp_allowed_p1 = model.DbGroupPermissionParameter(gp_allowed, permissions.EXPERIMENT_PERMANENT_ID, exp_name)
    session.add(gp_allowed_p1)
    gp_allowed_p2 = model.DbGroupPermissionParameter(gp_allowed, permissions.EXPERIMENT_CATEGORY_ID, cat_name)
    session.add(gp_allowed_p2)
    gp_allowed_p3 = model.DbGroupPermissionParameter(gp_allowed, permissions.TIME_ALLOWED, six.text_type(time))
    session.add(gp_allowed_p3)

def _grant_permissions_to_groups(session, groups_data, experiments_data, permissions_data):
    for args in permissions_data:
        _grant_permission_to_group(session, groups_data, experiments_data, *args)

def _grant_permission_to_user(session, users_data, experiments_data, login, exp_name, cat_name, time):
    if (exp_name, cat_name) not in experiments_data:
        raise Exception("Error: %s@%s not previously registered" % (exp_name, cat_name))

    db_user = users_data[login]

    up_allowed = model.DbUserPermission(
        db_user,
        permissions.EXPERIMENT_ALLOWED,
        "%s::%s" % (login, exp_name),
        datetime.datetime.utcnow(),
        "Permission for user %s to use %s" % (login, exp_name)
    )
    session.add(up_allowed)
    up_allowed_p1 = model.DbUserPermissionParameter(up_allowed, permissions.EXPERIMENT_PERMANENT_ID, exp_name)
    session.add(up_allowed_p1)
    up_allowed_p2 = model.DbUserPermissionParameter(up_allowed, permissions.EXPERIMENT_CATEGORY_ID, cat_name)
    session.add(up_allowed_p2)
    up_allowed_p3 = model.DbUserPermissionParameter(up_allowed, permissions.TIME_ALLOWED, six.text_type(time))
    session.add(up_allowed_p3)

def _grant_permissions_to_users(session, users_data, experiments_data, permissions_data):
    for args in permissions_data:
        _grant_permission_to_user(session, users_data, experiments_data, *args)

def populate_weblab_tests(engine, tests):
    Session = sessionmaker(bind=engine)
    Session._model_changes = {}
    session = Session()

    ldap = session.query(model.DbAuthType).filter_by(name="LDAP").one()
    iptrusted = session.query(model.DbAuthType).filter_by(name="TRUSTED-IP-ADDRESSES").one()
    facebook = session.query(model.DbAuthType).filter_by(name="FACEBOOK").one()

    # Auths
    cdk_ldap = model.DbAuth(ldap, "Configuration of CDK at Deusto", 2, "ldap_uri=ldaps://castor.cdk.deusto.es;domain=cdk.deusto.es;base=dc=cdk,dc=deusto,dc=es")
    session.add(cdk_ldap)

    deusto_ldap = model.DbAuth(ldap, "Configuration of DEUSTO at Deusto", 3, "ldap_uri=ldaps://altair.cdk.deusto.es;domain=deusto.es;base=dc=deusto,dc=es")
    session.add(deusto_ldap)

    localhost_ip = model.DbAuth(iptrusted, "trusting in localhost", 4, "127.0.0.1")
    session.add(localhost_ip)

    auth_facebook = model.DbAuth(facebook, "Facebook", 5)
    session.add(auth_facebook)

    administrator = session.query(model.DbRole).filter_by(name='administrator').one()
    instructor    = session.query(model.DbRole).filter_by(name='instructor').one()
    student       = session.query(model.DbRole).filter_by(name='student').one()
    federated     = session.query(model.DbRole).filter_by(name='federated').one()

    # Users
    # Please keep alphabetical order :-)
    all_users = _create_users(session, {
        'admin1'       : (administrator, 'Name of administrator 1',       'weblab@deusto.es'),
        'admin2'       : (administrator, 'Name of administrator 2',       'weblab@deusto.es'),
        'admin3'       : (administrator, 'Name of administrator 3',       'weblab@deusto.es'),

        'any'          : (student,       'Name of any',                   'weblab@deusto.es',  'password', None, [(auth_facebook, '1168497114')]),
        'admin'        : (administrator, 'Administrator',                 'weblab@deusto.es'),

        'archimedes'   : (student,       'Usuario de prueba para Splash', 'weblab@deusto.es',  'archimedes'),
        'consumer1'    : (federated,     'Consumer University 1',         'weblab@deusto.es'),
        'fedstudent1'  : (federated,     'Name of federated user 1',      'weblab@deusto.es'),
        'fedstudent2'  : (federated,     'Name of federated user 2',      'weblab@deusto.es'),
        'fedstudent3'  : (federated,     'Name of federated user 3',      'weblab@deusto.es'),
        'fedstudent4'  : (federated,     'Name of federated user 4',      'weblab@deusto.es'),

        'intstudent1'  : (student,       'Name of integration test 1',    'weblab@deusto.es'),
        'intstudent2'  : (student,       'Name of integration test 2',    'weblab@deusto.es'),
        'intstudent3'  : (student,       'Name of integration test 3',    'weblab@deusto.es'),
        'intstudent4'  : (student,       'Name of integration test 4',    'weblab@deusto.es'),
        'intstudent5'  : (student,       'Name of integration test 5',    'weblab@deusto.es'),
        'intstudent6'  : (student,       'Name of integration test 6',    'weblab@deusto.es'),

        'prof1'        : (instructor,    'Name of instructor 1',          'weblab@deusto.es'),
        'prof2'        : (instructor,    'Name of instructor 2',          'weblab@deusto.es'),
        'prof3'        : (instructor,    'Name of instructor 3',          'weblab@deusto.es'),
        'provider1'    : (federated,     'Provider University 1',         'weblab@deusto.es'),
        'provider2'    : (federated,     'Provider University 2',         'weblab@deusto.es'),

        'student1'     : (student,       'Name of student 1',             'weblab@deusto.es'),
        'student2'     : (student,       'Name of student 2',             'weblab@deusto.es'),
        'student3'     : (student,       'Name of student 3',             'weblab@deusto.es'),
        'student4'     : (student,       'Name of student 4',             'weblab@deusto.es'),
        'student5'     : (student,       'Name of student 5',             'weblab@deusto.es'),
        'student6'     : (student,       'Name of student 6',             'weblab@deusto.es'),
        'student7'     : (student,       'Name of student 7',             'weblab@deusto.es', None, 'aaaa{thishashdoesnotexist}a776159c8c7ff8b73e43aa54d081979e72511474'),
        'student8'     : (student,       'Name of student 8',             'weblab@deusto.es', None, 'this.format.is.not.valid.for.the.password'),
        'studentILAB'  : (student,       'Name of student ILAB',          'weblab@deusto.es'),
        'studentLDAP1' : (student,       'Name of student LDAP1',         'weblab@deusto.es', 'password', None, [(cdk_ldap, None)]),
        'studentLDAP2' : (student,       'Name of student LDAP2',         'weblab@deusto.es', 'password', None, [(cdk_ldap, None)]),
        'studentLDAP3' : (student,       'Name of student LDAP3',         'weblab@deusto.es', 'password', None, [(deusto_ldap, None)]),
    })

    # Please keep alphabetical order :-)
    all_groups = _create_groups(session, all_users, {
        ('Course 2008/09',    None)              : ('student1', 'student2'),
        ('Course 2009/10',    None)              : ('student1', 'student2', 'student3', 'student4', 'student5', 'student6'),
        ('Course Tests',      None)              : ('intstudent1', 'intstudent2', 'intstudent3', 'intstudent4', 'intstudent5', 'intstudent6'),
        ('Federated users',   None)              : ('fedstudent1', 'fedstudent2', 'fedstudent3', 'fedstudent4', 'consumer1', 'provider1', 'provider2'),
        ('Mechatronics',      'Course 2008/09')  : ('student3', 'student4'),
        ('Telecomunications', 'Course 2008/09')  : ('student5', 'student6'),
    })

    # Please keep alphabetical order :-)
    all_experiments = _create_experiments(session, {
        ('aquarium',                'Aquatic experiments')   : 'aquarium',
        ('aquariumjs',              'Aquatic experiments')   : 'js',
        ('archimedes',              'Aquatic experiments')   : 'js',
        ('binary',                  'Games')                 : 'binary',
        ('blink-led',               'LabVIEW experiments')   : 'labview',
        ('control-app',             'Control experiments')   : 'control-app',
        ('dummy1',                  'Dummy experiments')     : 'dummy',
        ('dummy2',                  'Dummy experiments')     : 'dummy',
        ('dummy4',                  'Dummy experiments')     : 'dummy',
        ('elevator',                'FPGA experiments')      : 'js',
        ('external-robot-movement', 'Robot experiments')     : 'blank',
        ('flashdummy',              'Dummy experiments')     : 'flash',
        ('http',                    'HTTP experiments')      : 'redirect',
        ('hwboard-fpga',            'FPGA experiments')      : 'js',
        ('hwboard-fpga-watertank',  'FPGA experiments')      : 'js',
        ('incubator',               'Farm experiments')      : 'incubator',
        ('new_incubator',           'Farm experiments')      : 'js',
        ('javadummy',               'Dummy experiments')     : 'java',
        ('jsdummy',                 'Dummy experiments')     : 'js',
        ('jsfpga',                  'FPGA experiments')      : 'js',
        ('microelectronics',        'iLab experiments')      : 'ilab-batch',
        ('robot-maze',              'Robot experiments')     : 'robot-maze',
        ('robot-movement',          'Robot experiments')     : 'robot-movement',
        ('robot-proglist',          'Robot experiments')     : 'robot-proglist',
        ('robot-standard',          'Robot experiments')     : 'robot-standard',
        ('robotarm',                'Robot experiments')     : 'robotarm',
        ('romie',                   'Robot experiments')     : 'js',
        ('romie_labpsico',          'Robot experiments')     : 'js',
        ('romie_demo',              'Robot experiments')     : 'js',
        ('romie_blockly',           'Robot experiments')     : 'js',
        ('submarine',               'Submarine experiments') : 'submarine',
        ('submarinejs',             'Aquatic experiments')   : 'js',
        ('ud-demo-fpga',            'FPGA experiments')      : 'xilinx',
        ('ud-demo-pld',             'PLD experiments')       : 'xilinx',
        ('ud-demo-xilinx',          'Xilinx experiments')    : 'xilinx',
        ('ud-dummy',                'Dummy experiments')     : 'js',
        ('ud-dummy-batch',          'Dummy experiments')     : 'dummybatch',
        ('ud-fpga',                 'FPGA experiments')      : 'xilinx',
        ('ud-gpib',                 'GPIB experiments')      : 'gpib',
        ('ud-logic',                'PIC experiments')       : 'logic',
        ('ud-pld',                  'PLD experiments')       : 'xilinx',
        ('ud-pic18',                'PIC experiments')       : 'pic18',
        ('unr-physics',             'Physics experiments')   : 'js',
        ('visir',                   'Visir experiments')     : 'visir',
        ('visir-html5',             'Visir experiments')     : 'js',
        ('visirtest',               'Dummy experiments')     : 'visir',
        ('vm',                      'Dummy experiments')     : 'vm',
        ('vm-win',                  'Dummy experiments')     : 'vm',
    })

    if tests != '2':
        all_experiments['dummy3', 'Dummy experiments'] = _create_experiment(session, 'dummy3', 'Dummy experiments', 'dummy')
    else:
        all_experiments['dummy3_with_other_name', 'Dummy experiments'] = _create_experiment(session, 'dummy3_with_other_name', 'Dummy experiments', 'dummy')


    # Please keep alphabetical order :-)
    _grant_permissions_to_groups(session, all_groups, all_experiments, [
        ('Course 2008/09',  'flashdummy',  'Dummy experiments',  30),
        ('Course 2008/09',  'javadummy',   'Dummy experiments',  30),
        ('Course 2008/09',  'ud-dummy',    'Dummy experiments', 150),
        ('Course 2008/09',  'ud-fpga',     'FPGA experiments',  300),
        ('Course 2008/09',  'ud-logic',    'PIC experiments',   150),

        ('Course 2009/10',  'ud-fpga',     'FPGA experiments',  300),

        ('Course Tests',    'dummy1',      'Dummy experiments',  300),
        ('Course Tests',    'dummy2',      'Dummy experiments',  300),

        ('Federated users', 'dummy1',      'Dummy experiments', 300),
        ('Federated users', 'dummy2',      'Dummy experiments', 300),
        ('Federated users', 'dummy4',      'Dummy experiments', 300),
    ])

    if tests != '2':
        _grant_permissions_to_groups(session, all_groups, all_experiments, [
            ('Federated users', 'dummy3',  'Dummy experiments', 300),
        ])
    else:
        _grant_permissions_to_groups(session, all_groups, all_experiments, [
            ('Federated users', 'dummy3_with_other_name',  'Dummy experiments', 300),
        ])


    # Please keep alphabetical order :-)
    _grant_permissions_to_users(session, all_users, all_experiments, [
        ('archimedes', 'archimedes',              'Aquatic experiments',   1400),

        ('any',        'aquarium',                'Aquatic experiments',    200),
        ('any',        'aquariumjs',              'Aquatic experiments',    200),
        ('any',        'binary',                  'Games',                  200),
        ('any',        'blink-led',               'LabVIEW experiments',    200),
        ('any',        'control-app',             'Control experiments',    200),
        ('any',        'elevator',                'FPGA experiments',      1400),
        ('any',        'external-robot-movement', 'Robot experiments',      200),
        ('any',        'http',                    'HTTP experiments',       200),
        ('any',        'hwboard-fpga',            'FPGA experiments',      1400),
        ('any',        'hwboard-fpga-watertank',  'FPGA experiments',      1400),
        ('any',        'new_incubator',           'Farm experiments',       300),
        ('any',        'jsdummy',                 'Dummy experiments',     1400),
        ('any',        'jsfpga',                  'FPGA experiments',      1400),
        ('any',        'microelectronics',        'iLab experiments',       200),
        ('any',        'robot-maze',              'Robot experiments',      200),
        ('any',        'robot-movement',          'Robot experiments',      200),
        ('any',        'robot-proglist',          'Robot experiments',      200),
        ('any',        'robot-standard',          'Robot experiments',      200),
        ('any',        'robotarm',                'Robot experiments',      200),
        ('any',        'romie',                   'Robot experiments',      1200),
        ('any',        'romie_labpsico',          'Robot experiments',      1800),
        ('any',        'romie_demo',              'Robot experiments',      1800),
        ('any',        'romie_blockly',           'Robot experiments',      1800),
        ('any',        'submarine',               'Submarine experiments',  200),
        ('any',        'submarinejs',             'Aquatic experiments',    200),
        ('any',        'ud-demo-fpga',            'FPGA experiments',       200),
        ('any',        'ud-demo-pld',             'PLD experiments',        200),
        ('any',        'ud-demo-xilinx',          'Xilinx experiments',     200),
        ('any',        'ud-dummy',                'Dummy experiments',      200),
        ('any',        'ud-dummy-batch',          'Dummy experiments',      200),
        ('any',        'ud-fpga',                 'FPGA experiments',      1400),
        ('any',        'ud-gpib',                 'GPIB experiments',       150),
        ('any',        'ud-logic',                'PIC experiments',        200),
        ('any',        'ud-pic18',                'PIC experiments',        200),
        ('any',        'unr-physics',             'Physics experiments',    200),
        ('any',        'visir',                   'Visir experiments',     3600),
        ('any',        'visir-html5',             'Visir experiments',     3600),
        ('any',        'visirtest',               'Dummy experiments',     3600),
        ('any',        'vm',                      'Dummy experiments',      200),
        ('any',        'vm-win',                  'Dummy experiments',      200),

        ('student2',   'ud-gpib',                 'GPIB experiments',       150),
        ('student2',   'ud-pld',                  'PLD experiments',        100),
        ('student6',   'ud-pld',                  'PLD experiments',        140),
    ])

    # Other permissions
    up_student1_admin_panel_access = model.DbUserPermission(
        all_users['student1'],
        permissions.ADMIN_PANEL_ACCESS,
        "student1::admin_panel_access",
        datetime.datetime.utcnow(),
        "Access to the admin panel for student1 with full_privileges"
    )
    session.add(up_student1_admin_panel_access)
    up_student1_admin_panel_access_p1 = model.DbUserPermissionParameter(up_student1_admin_panel_access, permissions.FULL_PRIVILEGES, True)
    session.add(up_student1_admin_panel_access_p1)

    up_any_access_forward = model.DbUserPermission(
        all_users['any'],
        permissions.ACCESS_FORWARD,
        "any::access_forward",
        datetime.datetime.utcnow(),
        "Access to forward external accesses"
    )

    session.add(up_any_access_forward)

    client_properties = {
        "demo.available": True,
        "admin.email": "weblab@deusto.es",
        "google.analytics.tracking.code": "UA-1234567-8",
        "host.entity.link": "http://www.deusto.es/",
    }
    
    for key, value in six.iteritems(client_properties):
        session.add(model.DbClientProperties(key, value))

    session.commit()

def generate_create_database(engine_str):
    "Generate a create_database function that creates the database"

    if engine_str == 'sqlite':

        import sqlite3
        dbi = sqlite3
        def create_database_sqlite(admin_username, admin_password, database_name, new_user, new_password, host = "localhost", port = None, db_dir = '.'):
            fname = os.path.join(db_dir, '%s.db' % database_name)
            if os.path.exists(fname):
                os.remove(fname)
            sqlite3.connect(database = fname).close()
        return create_database_sqlite

    elif engine_str == 'mysql':

        try:
            import MySQLdb
            dbi = MySQLdb
        except ImportError:
            try:
                import pymysql_sa
            except ImportError:
                raise Exception("Neither MySQLdb nor pymysql have been installed. First install them by running 'pip install pymysql' or 'pip install python-mysql'")
            pymysql_sa.make_default_mysql_dialect()
            import pymysql
            dbi = pymysql

        def create_database_mysql(error_message, admin_username, admin_password, database_name, new_user, new_password, host = "localhost", port = None, db_dir = '.'):
            args = {
                    'DATABASE_NAME' : database_name,
                    'USER'          : new_user,
                    'PASSWORD'      : new_password,
                }


            sentence1 = "DROP DATABASE IF EXISTS %(DATABASE_NAME)s;" % args
            sentence2 = "CREATE DATABASE %(DATABASE_NAME)s;" % args
            sentence3 = "GRANT ALL ON %(DATABASE_NAME)s.* TO '%(USER)s'@'%%' IDENTIFIED BY '%(PASSWORD)s';" % args
            sentence4 = "GRANT ALL ON %(DATABASE_NAME)s.* TO '%(USER)s'@'localhost' IDENTIFIED BY '%(PASSWORD)s';" % args
            sentence5 = "FLUSH PRIVILEGES;" % args

            try:
                kwargs = dict(db=database_name, user = admin_username, passwd = admin_password, host = host)
                if port is not None:
                    kwargs['port'] = port
                dbi.connect(**kwargs).close()
            except Exception, e:
                if e[1].startswith("Unknown database"):
                    sentence1 = "SELECT 1"

            for sentence in (sentence1, sentence2, sentence3, sentence4, sentence5):
                try:
                    kwargs = dict(user = admin_username, passwd = admin_password, host = host)
                    if port is not None:
                        kwargs['port'] = port
                    connection = dbi.connect(**kwargs)
                except dbi.OperationalError:
                    traceback.print_exc()
                    print("", file=sys.stderr)
                    print("    %s" % error_message, file=sys.stderr)
                    print("", file=sys.stderr)
                    sys.exit(-1)
                else:
                    cursor = connection.cursor()
                    cursor.execute(sentence)
                    connection.commit()
                    connection.close()
        return create_database_mysql

    else:
        return None

def add_user(sessionmaker, login, password, user_name, mail, randomstuff = None, role = 'student'):
    sessionmaker._model_changes = {}
    session = sessionmaker()

    role = session.query(model.DbRole).filter_by(name=role).one()
    weblab_db = session.query(model.DbAuth).filter_by(name = "WebLab DB").one()

    user    = model.DbUser(login, user_name, mail, None, role)
    session.add(user)

    user_auth = model.DbUserAuth(user, weblab_db, password2sha(password, randomstuff))
    session.add(user_auth)

    session.commit()
    session.close()

def add_group(sessionmaker, group_name):
    sessionmaker._model_changes = {}  # flask-sqlalchemy bug bypass
    session = sessionmaker()
    group = model.DbGroup(group_name)
    session.add(group)
    session.commit()
    session.close()

def add_users_to_group(sessionmaker, group_name, *user_logins):
    sessionmaker._model_changes = {}  # flask-sqlalchemy bug bypass
    session = sessionmaker()
    group = session.query(model.DbGroup).filter_by(name = group_name).one()
    users = session.query(model.DbUser).filter(model.DbUser.login.in_(user_logins)).all()
    for user in users:
        group.users.append(user)
    session.commit()
    session.close()

def add_experiment(sessionmaker, category_name, experiment_name, client, params = None):
    sessionmaker._model_changes = {}  # flask-sqlalchemy bug bypass
    session = sessionmaker()
    existing_category = session.query(model.DbExperimentCategory).filter_by(name = category_name).first()
    if existing_category is None:
        category = model.DbExperimentCategory(category_name)
        session.add(category)
    else:
        category = existing_category

    start_date = datetime.datetime.utcnow()
    # So leap years are not a problem
    end_date = start_date.replace(year=start_date.year+12)

    experiment = model.DbExperiment(experiment_name, category, start_date, end_date, client)
    _add_params(session, experiment, params)
    session.add(experiment)
    session.commit()
    session.close()

def grant_experiment_on_group(sessionmaker, category_name, experiment_name, group_name, time_allowed):
    sessionmaker._model_changes = {}  # flask-sqlalchemy bug bypass
    session = sessionmaker()

    group = session.query(model.DbGroup).filter_by(name = group_name).one()

    experiment_allowed = permissions.EXPERIMENT_ALLOWED

    experiment_allowed_p1 = permissions.EXPERIMENT_PERMANENT_ID
    experiment_allowed_p2 = permissions.EXPERIMENT_CATEGORY_ID
    experiment_allowed_p3 = permissions.TIME_ALLOWED

    group_permission = model.DbGroupPermission(
        group, experiment_allowed,
        "%s users::%s@%s" % (group_name, experiment_name, category_name),
        datetime.datetime.utcnow(),
        "Permission for group %s users to use %s@%s" % (group_name, experiment_name, category_name))

    session.add(group_permission)

    group_permission_p1 = model.DbGroupPermissionParameter(group_permission, experiment_allowed_p1, experiment_name)
    session.add(group_permission_p1)

    group_permission_p2 = model.DbGroupPermissionParameter(group_permission, experiment_allowed_p2, category_name)
    session.add(group_permission_p2)

    group_permission_p3 = model.DbGroupPermissionParameter(group_permission, experiment_allowed_p3, str(time_allowed))
    session.add(group_permission_p3)

    session.commit()
    session.close()

def grant_admin_panel_on_group(sessionmaker, group_name):
    session = sessionmaker()

    permission_type = permissions.ADMIN_PANEL_ACCESS
    group = session.query(model.DbGroup).filter_by(name = group_name).one()
    group_permission = model.DbGroupPermission(
                                    group,
                                    permission_type,
                                    'Administrators:admin-panel', datetime.datetime.now(), ''
                                )
    session.add(group_permission)
    group_permission_p1 = model.DbGroupPermissionParameter(
                                    group_permission,
                                    permissions.FULL_PRIVILEGES,
                                    True
                                )
    session.add(group_permission_p1)
    session.commit()
    session.close()


def add_experiment_and_grant_on_group(sessionmaker, category_name, experiment_name, client, group_name, time_allowed, params = None):
    add_experiment(sessionmaker, category_name, experiment_name, client, params)
    grant_experiment_on_group(sessionmaker, category_name, experiment_name, group_name, time_allowed)

def add_client_config(sessionmaker, configuration_js):
    session = sessionmaker()

    for key, value in configuration_js.items():
        new_properties = model.DbClientProperties(key, value)
        session.add(new_properties)

    session.commit()
    session.close()
