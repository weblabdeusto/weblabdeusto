#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009 University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals, 
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
# 
import unittest
import json

import time
import urllib2
import datetime

from weblab.data.dto.experiments import ExperimentUse
from weblab.data.dto.experiments    import Experiment
from weblab.data.dto.experiments      import ExperimentCategory
from weblab.data.dto.users         import Group
from weblab.data.dto.users          import User
from weblab.data.dto.users          import Role

import weblab.comm.server as RemoteFacadeServer
import weblab.core.comm.admin_server as AdminFacadeServer

import voodoo.configuration as ConfigurationManager
import test.unit.configuration as configuration

from test.util.module_disposer import uses_module

import mocker

USERNAME ='myusername'
PASSWORD ='mypassword'
REAL_ID  ='this_is_the_real_id'

class SmartGwtClient(object):
    def __init__(self, port):
        self.port = port

    def get_groups(self, session_id, parent_id = 'not_provided'):
        # 
        # Input:
        #   GET /data/groups_fetch.js?parent_id=null&sessionid=2xKszwgw-MRSCRfO HTTP/1.1
        # 
        # Output:
        #   [ { "id": 1, "name": "Course 2008/09", "parent_id": null, "isFolder": true}, ... ]
        # 
        options = { 'parent_id' : str(parent_id) if parent_id is not None else "null", 'sessionid' : session_id}
        if parent_id == 'not_provided':
            options.pop('parent_id')
        urlobj  = self._open("/data/groups", options)
        content = urlobj.read()
        return json.loads(content)['response']['data']
    
#    def update_groups(self, session_id, id, name, parent_id):
#        # 
#        # Input:
#        #   GET /data/groups_update.js?id=1&name=newName&parent_id=null&sessionid=2xKszwgw-MRSCRfO HTTP/1.1
#        # 
#        # Output:
#        #   [ { "id": 1, "name": "newName", "parent_id": null, "isFolder": true}, ... ]
#        # 
#        options = { 'parent_id' : str(parent_id) if parent_id is not None else "null", 'sessionid' : session_id}
#        if parent_id == 'not_provided':
#            options.pop('parent_id')
#        urlobj  = self._open("/data/groups", options)
#        content = urlobj.read()
#        return json.loads(content)['response']['data']

    def get_experiments(self, session_id):
        # 
        # Input:
        #   GET /data/experiments_fetch.js?sessionid=2xKszwgw-MRSCRfO HTTP/1.1
        # 
        # Output:
        #  [ { "id": 1, "name": "ud-fpga", "category": "FPGA experiments" }, ... ]
        # 
        urlobj  = self._open("/data/experiments", { 'sessionid' : session_id })
        content = urlobj.read()
        return json.loads(content)['response']['data']

    def get_experiment_uses(self, session_id, criterias, operator, start_row, end_row, sort_by, text_match_style):
        #
        # Input:
        #   GET /weblab/administration/json/experiment_uses?sessionid=srZg6n-05Xu0GaPk&operator=and&_constructor=AdvancedCriteria&criteria=%7B%22fieldName%22%3A%22start_date%22%2C%22operator%22%3A%22greaterOrEqual%22%2C%22value%22%3A%222010-10-03T22%3A00%3A00%22%7D&criteria=%7B%22fieldName%22%3A%22end_date%22%2C%22operator%22%3A%22lessOrEqual%22%2C%22value%22%3A%222010-10-08T21%3A59%3A59%22%7D&criteria=%7B%22fieldName%22%3A%22groups%22%2C%22operator%22%3A%22inSet%22%2C%22value%22%3A2%7D&criteria=%7B%22fieldName%22%3A%22experiment_id%22%2C%22operator%22%3A%22equals%22%2C%22value%22%3A9%7D&_operationType=fetch&_startRow=0&_endRow=50&_sortBy=start_date&_textMatchStyle=exact&_componentId=isc_ListGrid_5&_dataSource=isc_ExperimentUsesDataSource_0  HTTP/1.0
        # 
        # Input translated:
        # 
        #   GET /weblab/administration/json/experiment_uses
        #                ?sessionid=srZg6n-05Xu0GaPk
        #                &operator=and&_constructor=AdvancedCriteria
        #                &criteria={'operator': 'greaterOrEqual', 'fieldName': 'start_date',    'value': '2010-10-03T22:00:00'}
        #                &criteria={'operator': 'lessOrEqual',    'fieldName': 'end_date',      'value': '2010-10-08T21:59:59'}
        #                &criteria={'operator': 'equals',         'fieldName': 'group',         'value': 2}
        #                &criteria={'operator': 'equals',         'fieldName': 'experiment_id', 'value': 9}
        #                &_operationType=fetch
        #                &_startRow=0
        #                &_endRow=50
        #                &_sortBy=start_date
        #                &_textMatchStyle=exact
        #                &_componentId=isc_ListGrid_5
        #                &_dataSource=isc_ExperimentUsesDataSource_0  HTTP/1.0
        #
        # Output:
        #  {
        # ."response":
        # .{
        # .."status": 0,
        # .."startRows": 0,
        # .."endRow": 4,
        # .."totalRows": 4,
        # .."data":
        # ..[
        # ...{
        # ...."id": 1,
        # ...."start_date": "2010-06-15T06:51:40",
        # ...."end_date": "2010-06-15T06:51:45",
        # ...."agent_login": "student1",
        # ...."agent_name": "Name of student 1",
        # ...."agent_email": "weblab@deusto.es",
        # ...."experiment_name": "ud-dummy",
        # ...."experiment_category": "Dummy experiments",
        # ...."origin": "unknown",
        # ...},
        # ...{
        # ...."id": 2,
        # ...."start_date": "2010-06-16T06:51:40",
        # ...."end_date": "2010-06-16T06:51:45",
        # ...."agent_login": "student2",
        # ...."agent_name": "Name of student 2",
        # ...."agent_email": "weblab@deusto.es",
        # ...."experiment_name": "ud-fpga",
        # ...."experiment_category": "FPGA experiments",
        # ...."origin": "unknown",
        #    ...
        #    ...
        # ..]
        # .}
        # }
        # 
        data = {
                'sessionid'  : session_id,
                '_startRow'  : start_row,
                '_endRow'    : end_row,
                '_sortBy'    : [ sorter for sorter in sort_by ],
                '_textMatchStyle' : text_match_style,
                'criteria'        : [ json.dumps(criteria) for criteria in criterias ],
                '_operationType'  : 'fetch',
                '_componentId'    : 'isc_ListGrid_5',
                '_dataSource'     : 'isc_ExperimentUsesDataSource_0',
                '_constructor'    : 'AdvancedCriteria'
            }
        if operator is not None:
            data['operator'] = operator
        urlobj = self._open('/data/experiment_uses', data)
        content = urlobj.read()
        return json.loads(content)['response']

    def _open(self, path, options):
        parsed_options = []
        for option in options:
            if isinstance(options[option], (list, tuple)):
                for new_option in options[option]:
                    key = urllib2.quote(str(option))
                    value = urllib2.quote(str(new_option))
                    parsed_options.append("%s=%s" % (key, value))
            else:        
                key = urllib2.quote(str(option))
                value = urllib2.quote(str(options[option]))
                parsed_options.append("%s=%s" % (key, value))
        url = "http://localhost:%s/%s?%s" % (self.port, path, '&'.join(parsed_options))
        return urllib2.urlopen(url)

class AdminRemoteFacadeServerTestCase(unittest.TestCase):
    def setUp(self):
        self.configurationManager = ConfigurationManager.ConfigurationManager()
        self.configurationManager.append_module(configuration)
        self.configurationManager._set_value(RemoteFacadeServer.RFS_TIMEOUT_NAME, 0.01)

        time.sleep( 0.01 * 5 )

        self.configurationManager._set_value(AdminFacadeServer.ADMIN_FACADE_JSON_LISTEN, '')

        self.mocker   = mocker.Mocker()
        self.rfm_json = self.mocker.mock()

        class WrappedRemoteFacadeServer(AdminFacadeServer.AdminRemoteFacadeServer):
            def _create_smartgwt_remote_facade_manager(inner_self, *args, **kwargs):
                return self.rfm_json

        self.rfs = WrappedRemoteFacadeServer(None, self.configurationManager)
        
    @uses_module(RemoteFacadeServer)
    def test_get_experiments(self):
        PORT = 11224
        self.configurationManager._set_value(AdminFacadeServer.ADMIN_FACADE_JSON_PORT, PORT)
        self.client = SmartGwtClient(PORT)
        self.rfs.start()
        try:
            self.rfm_json.get_experiments({ 'id' : REAL_ID})
            dt = datetime.datetime.now()
            experiments = [ Experiment("ud-pld", ExperimentCategory("PLD experiments"), dt, dt, id=1), Experiment("ud-fpga", ExperimentCategory("FPGA experiments"), dt, dt, id=2) ]
            self.mocker.result(experiments)
            self.mocker.replay()

            experiments = self.client.get_experiments(REAL_ID)

            self.assertEquals(2, len(experiments))

            self.assertEquals("ud-pld", experiments[0]['name'])
            self.assertEquals("PLD experiments", experiments[0]['category'])
            self.assertEquals(1, experiments[0]['id'])

            self.assertEquals("ud-fpga", experiments[1]['name'])
            self.assertEquals("FPGA experiments", experiments[1]['category'])
            self.assertEquals(2, experiments[1]['id'])

            self.mocker.verify()
        finally:
            self.rfs.stop()

    @uses_module(RemoteFacadeServer)
    def test_get_groups(self):
        PORT = 11225
        self.configurationManager._set_value(AdminFacadeServer.ADMIN_FACADE_JSON_PORT, PORT)
        self.client = SmartGwtClient(PORT)
        self.rfs.start()
        try:

            # TODO 
            parent = Group("parent", id = 5)
            child1 = Group("child1", id = 7)
            child2 = Group("child2", id = 9)
            parent.add_child(child1)
            parent.add_child(child2)

            self.rfm_json.get_groups({ 'id' : REAL_ID}, 5)

            groups = [ child1, child2 ]
            self.mocker.result(groups)

            self.rfm_json.get_groups({ 'id' : REAL_ID}, None)

            groups = [ parent ]
            self.mocker.result(groups)

            self.mocker.replay()

            groups = self.client.get_groups(REAL_ID, 5)

            self.assertEquals(2,        len(groups))

            self.assertEquals(7,        groups[0]['id'])
            self.assertEquals('child1', groups[0]['name'])
            self.assertEquals(5,        groups[0]['parent_id'])
            self.assertEquals(False,    groups[0]['isFolder'])

            self.assertEquals(9,        groups[1]['id'])
            self.assertEquals('child2', groups[1]['name'])
            self.assertEquals(5,        groups[1]['parent_id'])
            self.assertEquals(False,    groups[1]['isFolder'])


            groups = self.client.get_groups(REAL_ID, None)

            self.assertEquals(1,        len(groups))

            self.assertEquals(5,        groups[0]['id'])
            self.assertEquals('parent', groups[0]['name'])
            self.assertEquals(None,     groups[0]['parent_id'])
            self.assertEquals(True,     groups[0]['isFolder'])

            try:
                groups = self.client.get_groups(REAL_ID, 'foo')
                self.fail("HTTPError expected")
            except urllib2.HTTPError as error:
                self.assertEquals(400, error.code)
                self.assertTrue(error.read().find("int") >= 0)

            try:
                groups = self.client.get_groups(REAL_ID)
                self.fail("HTTPError expected")
            except urllib2.HTTPError as error:
                self.assertEquals(400, error.code)
                self.assertTrue(error.read().find("provided") >= 0)

            self.mocker.verify()
        finally:
            self.rfs.stop()

    @uses_module(RemoteFacadeServer)
    def test_get_experiment_uses(self):
        PORT = 11226
        self.configurationManager._set_value(AdminFacadeServer.ADMIN_FACADE_JSON_PORT, PORT)
        self.client = SmartGwtClient(PORT)
        self.rfs.start()
        try:

            criterias = []
            criterias.append({
                    'operator'  : 'greaterOrEqual',
                    'fieldName' : 'start_date',
                    'value'     : '2010-10-03T22:00:00'
                })
            criterias.append({
                    'operator'  : 'lessOrEqual',
                    'fieldName' : 'end_date',
                    'value'     : '2010-10-08T21:59:59'
                })
            criterias.append({
                    'operator'  : 'equals',
                    'fieldName' : 'group',
                    'value'     : 2
                })
            criterias.append({
                    'operator'  : 'equals',
                    'fieldName' : 'experiment_id',
                    'value'     : 9
                })

            from_date = datetime.datetime(2010, 10, 3, 22, 00, 00)
            to_date = datetime.datetime(2010, 10, 8, 21, 59, 59)

            dt1 = datetime.datetime(2010, 10, 4, 11, 00, 00)
            dt2 = datetime.datetime(2010, 10, 5, 12, 00, 00)

            user1 = User( "jaime.irurzun", "Jaime Irurzun", "jaime.irurzun@opendeusto.es", Role("student"))
            user2 = User( "pablo.orduna",  "Pablo Orduna",  "pablo.orduna@opendeusto.es",  Role("student"))

            exp = Experiment("ud-pld", ExperimentCategory("PLD experiments"), dt1, dt2, id=1)

            experiment_use1 = ExperimentUse(dt1, dt2, exp, user1, "unknown", id=4)
            experiment_use2 = ExperimentUse(dt1, dt2, exp, user2, "unknown", id=5)

            self.rfm_json.get_experiment_uses({ 'id' : REAL_ID}, from_date, to_date, 2, 9, 0, 50, ['start_date'])

            self.mocker.result(([experiment_use1, experiment_use2], 2))
            self.mocker.replay()

            experiment_uses_response = self.client.get_experiment_uses(REAL_ID, criterias, 'and', 0, 50, ['start_date'], 'exact')

            self.assertEquals(0,        experiment_uses_response['status'])
            self.assertEquals(0,        experiment_uses_response['startRows'])
            self.assertEquals(2,        experiment_uses_response['endRow'])
            self.assertEquals(2,        experiment_uses_response['totalRows'])
            
            experiment_uses = experiment_uses_response['data']

            self.assertEquals(2,        len(experiment_uses))

            self.assertEquals(4,                      experiment_uses[0]['id'])
            self.assertEquals('2010-10-04T11:00:00',  experiment_uses[0]['start_date'])
            self.assertEquals('2010-10-05T12:00:00',  experiment_uses[0]['end_date'])
            self.assertEquals(user1.login,            experiment_uses[0]['agent_login'])
            self.assertEquals(user1.full_name,        experiment_uses[0]['agent_name'])
            self.assertEquals(user1.email,            experiment_uses[0]['agent_email'])
            self.assertEquals('ud-pld',               experiment_uses[0]['experiment_name'])
            self.assertEquals('PLD experiments',      experiment_uses[0]['experiment_category'])
            self.assertEquals('unknown',              experiment_uses[0]['origin'])

            self.assertEquals(5,                      experiment_uses[1]['id'])
            self.assertEquals('2010-10-04T11:00:00',  experiment_uses[1]['start_date'])
            self.assertEquals('2010-10-05T12:00:00',  experiment_uses[1]['end_date'])
            self.assertEquals(user2.login,            experiment_uses[1]['agent_login'])
            self.assertEquals(user2.full_name,        experiment_uses[1]['agent_name'])
            self.assertEquals(user2.email,            experiment_uses[1]['agent_email'])
            self.assertEquals('ud-pld',               experiment_uses[1]['experiment_name'])
            self.assertEquals('PLD experiments',      experiment_uses[1]['experiment_category'])
            self.assertEquals('unknown',              experiment_uses[1]['origin'])

            self.mocker.verify()
        finally:
            self.rfs.stop()

    @uses_module(RemoteFacadeServer)
    def test_get_experiment_uses_without_criterias(self):
        PORT = 11227
        self.configurationManager._set_value(AdminFacadeServer.ADMIN_FACADE_JSON_PORT, PORT)
        self.client = SmartGwtClient(PORT)
        self.rfs.start()
        try:
            dt1 = datetime.datetime(2010, 10, 4, 11, 00, 00)
            dt2 = datetime.datetime(2010, 10, 5, 12, 00, 00)

            user1 = User( "jaime.irurzun", "Jaime Irurzun", "jaime.irurzun@opendeusto.es", Role("student"))
            user2 = User( "pablo.orduna",  "Pablo Orduna",  "pablo.orduna@opendeusto.es",  Role("student"))

            exp = Experiment("ud-pld", ExperimentCategory("PLD experiments"), dt1, dt2, id=1)

            experiment_use1 = ExperimentUse(dt1, dt2, exp, user1, "unknown", id=4)
            experiment_use2 = ExperimentUse(dt1, dt2, exp, user2, "unknown", id=5)

            self.rfm_json.get_experiment_uses({ 'id' : REAL_ID}, None, None, None, None, 0, 50, [])

            self.mocker.result(([experiment_use1, experiment_use2], 2))
            self.mocker.replay()

            experiment_uses_response = self.client.get_experiment_uses(REAL_ID, [], None, 0, 50, [], 'exact')

            self.assertEquals(0,        experiment_uses_response['status'])
            self.assertEquals(0,        experiment_uses_response['startRows'])
            self.assertEquals(2,        experiment_uses_response['endRow'])
            self.assertEquals(2,        experiment_uses_response['totalRows'])
            
            experiment_uses = experiment_uses_response['data']

            self.assertEquals(2,        len(experiment_uses))

            self.assertEquals(4,                      experiment_uses[0]['id'])
            self.assertEquals('2010-10-04T11:00:00',  experiment_uses[0]['start_date'])
            self.assertEquals('2010-10-05T12:00:00',  experiment_uses[0]['end_date'])
            self.assertEquals(user1.login,            experiment_uses[0]['agent_login'])
            self.assertEquals(user1.full_name,        experiment_uses[0]['agent_name'])
            self.assertEquals(user1.email,            experiment_uses[0]['agent_email'])
            self.assertEquals('ud-pld',               experiment_uses[0]['experiment_name'])
            self.assertEquals('PLD experiments',      experiment_uses[0]['experiment_category'])
            self.assertEquals('unknown',              experiment_uses[0]['origin'])

            self.assertEquals(5,                      experiment_uses[1]['id'])
            self.assertEquals('2010-10-04T11:00:00',  experiment_uses[1]['start_date'])
            self.assertEquals('2010-10-05T12:00:00',  experiment_uses[1]['end_date'])
            self.assertEquals(user2.login,            experiment_uses[1]['agent_login'])
            self.assertEquals(user2.full_name,        experiment_uses[1]['agent_name'])
            self.assertEquals(user2.email,            experiment_uses[1]['agent_email'])
            self.assertEquals('ud-pld',               experiment_uses[1]['experiment_name'])
            self.assertEquals('PLD experiments',      experiment_uses[1]['experiment_category'])
            self.assertEquals('unknown',              experiment_uses[1]['origin'])

            self.mocker.verify()
        finally:
            self.rfs.stop()
def suite():
    return unittest.makeSuite(AdminRemoteFacadeServerTestCase)

if __name__ == '__main__':
    unittest.main()

