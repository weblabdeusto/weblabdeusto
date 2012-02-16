#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

import datetime
import operator
import urllib
import urllib2

import json
import BaseHTTPServer

from weblab.comm.server import RemoteFacadeServerJSON
from weblab.comm.context import get_context, create_context, delete_context

import voodoo.log as log

class Criteria(object):
    """
    Describes a basic server-side Criteria which can be used with
    the client-side SmartGWT Criteria that is used for filtering
    within queries
    """

    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
    DATETIME_FIELDS = ('start_date', 'end_date')
    INT_FIELDS      = ('group','experiment_id')
    FIELDS          = DATETIME_FIELDS + INT_FIELDS

    def __init__(self, field_name, operator, value):
        self.field_name = field_name
        self.operator   = operator
        self.value      = value

    @staticmethod
    def parse(request):
        """
        parse(request)
        Deserializes a Criteria. Criterias used by SmartGWT are serialized
        to a specific JSON code, which this method is able to parse.
        """
        # It's actually JSON
        # criteria={"fieldName":"start_date","operator":"greaterOrEqual","value":"2010-06-08T22:00:00"}
        # criteria={"fieldName":"end_date","operator":"lessOrEqual","value":"2010-09-24T21:59:59"}
        # criteria={"fieldName":"groups","operator":"inSet","value":2}
        # criteria={"fieldName":"experiment_id","operator":"equals","value":"ud-fpga"}
        json_payload = request[request.find("=") + 1:]
        obj = json.loads(json_payload)
        try:
            field_name   = obj['fieldName']
            str_operator = obj["operator"]
            str_value    = obj['value']
        except KeyError as ke:
            raise MethodException("Missing criteria field: %s" % ke)

        try:
            if field_name in Criteria.DATETIME_FIELDS:
                value = datetime.datetime.strptime(str_value, Criteria.DATETIME_FORMAT)
            elif field_name in Criteria.INT_FIELDS:
                value = int(str_value)
            else:
                raise MethodException("Unrecognized field name! %s" % urllib2.quote(field_name))
        except ValueError as ve:
            raise MethodException("Couldn't parse value! %s" % ve)

        if str_operator == 'greaterOrEqual':
            op = operator.ge
        elif str_operator == 'lessOrEqual':
            op = operator.le
        elif str_operator == 'equals':
            op = operator.eq
        else:
            raise MethodException("Unrecognized operator!")

        return Criteria( field_name, op, value )

    def __str__(self):
        return "<Criteria field_name='%s' operator='%s' value='%s' />" % (self.field_name, self.operator, self.value)

class AdvancedCriteria(object):
    """
    Describes an advanced server-side Criteria which can be used with
    the client-side SmartGWT AdvancedCriteria that is used for filtering
    within queries
    """

    def __init__(self, criterias, operator, sort_by, start_row, end_row, text_match_style):
        self.criterias        = criterias
        self.operator         = operator
        self.sort_by          = sort_by
        self.start_row        = start_row
        self.end_row          = end_row
        self.text_match_style = text_match_style

    @staticmethod
    def parse(parameters):
        """
        parse(request)
        Deserializes an AdvancedCriteria. AdvancedCriterias used by SmartGWT are serialized
        to a specific JSON code, which this method is able to parse.
        """
        filter_parameter = lambda name : [ param[param.find('=') + 1:] for param in parameters if param.startswith(name + '=') ]
        parsed_criterias = map(lambda x: Criteria.parse(x), filter_parameter('criteria')) # [ crit1, crit2, crit3...]
        criterias  = dict([ (criteria.field_name, criteria) for criteria in parsed_criterias ]) # { criteria_name : Criteria object }
        start_rows = filter_parameter('_startRow')
        end_rows   = filter_parameter('_endRow')
        operators  = filter_parameter('operator')
        sort_by    = filter_parameter('_sortBy')
        text_match_styles = filter_parameter('_textMatchStyle')

        try:
            start_row = int(start_rows[0])
            end_row   = int(end_rows[0])
            if len(criterias) > 1:
                if operators[0] == 'and':
                    op = operator.and_
                else:
                    raise MethodException("Invalid advanced_criteria operator %s" % urllib2.quote(operators[0]))
            else:
                op = None
        except (ValueError, IndexError) as e:
            raise MethodException("Invalid advanced criteria value: %s" % urllib2.quote(str(e)))

        return AdvancedCriteria(criterias, op, sort_by, start_row, end_row, text_match_styles[0])


    def __str__(self):
        representation = "<AdvancedCriteria start_row='%s' end_row='%s' sort_by='%s' operator='%s'>" % (self.start_row, self.end_row, self.sort_by, self.operator)
        for criteria in self.criterias.values():
            representation += "\n\t" + str(criteria)
        return representation + "\n</AdvancedCriteria>"

class MethodException(Exception):
    pass

class Methods(object):
    """
    Methods is a class which simply encompasses the static server-side
    methods that are required to handle queries from the SmartGWT admin
    panel data sources. These queries are encoded in a SmartGWT specific
    JSON, so they must be parsed and an appropriate JSON response
    generated. They are the first server-side layer to receive them.
    """

    @staticmethod
    def get_experiments(handler, session_id, parameters):
        request_args = { 'id' : session_id }
        experiments = handler.facade_manager.get_experiments(request_args)
        return { 'response' :
                    { 'data' :
                        [
                            {
                                'id' : exp.id,
                                'name' : exp.name,
                                'category' : exp.category.name
                            }
                            for exp in experiments
                        ]
                    }
                }

    @staticmethod
    def get_permission_types(handler, session_id, parameters):
        """
        get_permission_types(handler, session_id, parameters)

        Retrieves permission types, returning them in a JSON-encoded string
        which will be understood by the client-side SmartGWT data source.
        """
        request_args = { 'id' : session_id }
        permission_types = handler.facade_manager.get_permission_types(request_args)
        return { 'response' :
            { 'data' :
                [
                    {
                        'name'  : ptype.name,
                        'description' : ptype.description,
                        'user_applicable_id' : ptype.user_applicable_id,
                        'group_applicable_id' : ptype.group_applicable_id,
                        'ee_applicable_id' : ptype.ee_applicable_id
                    }
                    for ptype in permission_types
                ]
            }
        }

    @staticmethod
    def get_roles(handler, session_id, parameters):
        """
        get_roles(handler, session_id, parameters)

        Retrieves roles, returning them in a JSON-encoded string which will be
        understood by the client-side SmartGWT data source.
        """
        request_args = { 'id' : session_id }
        roles = handler.facade_manager.get_roles(request_args)
        return { 'response' :
                    { 'data' :
                        [
                            {
                                'name' : role.name
                            }
                            for role in roles
                        ]
                    }
                }

    @staticmethod
    def get_user_permissions(handler, session_id, parameters):
        """
        get_user_permissions(handler, session_id, parameters)

        Retrieves user permissions, returning them in a JSON-encoded string
        which will be understood by the client-side SmartGWT data source.
        """
        request_args = { 'id' : session_id }
        user_permissions = handler.facade_manager.get_user_permissions(request_args)
        return { 'response' :
                    { 'data' :
                        [
                            {
                                # TODO: Consider what to to with this id. The DTO currently does not store
                                # the id. This follows the trend set by most DTOs. As of now, the client
                                # uses it though, but it might be possible to replace it with the permanent
                                # id.
                                'id' : up.permanent_id,
                                'user_id' : up.user_id,
                                'applicable_permission_type_id' : up.email,
                                'permanent_id' : up.permanent_id,
                                'date' : up.date,
                                'comments' : up.comments
                            }
                            for up in user_permissions
                        ]
                    }
                }

    @staticmethod
    def get_users(handler, session_id, parameters):
        """
        get_users(handler, session_id, parameters)

        Retrieves users, returning them in a JSON-encoded string which will be
        understood by the client-side SmartGWT data source.
        """
        request_args = { 'id' : session_id }
        users = handler.facade_manager.get_users(request_args)
        return { 'response' :
                    { 'data' :
                        [
                            {
                                'login' : user.login,
                                'full_name' : user.full_name,
                                'email' : user.email,
                                'avatar' : "",
                                'role' : user.role.name
                            }
                            for user in users
                        ]
                    }
                }

    @staticmethod
    def get_groups(handler, session_id, parameters):
        session_id = { 'id' : session_id }
        parent_ids = [ param for param in parameters if param.startswith('parent_id=') ]

        if len(parent_ids) == 0:
            raise MethodException("No parent_id provided")

        parent_id_str = parent_ids[0][len('parent_id') + 1:]
        try:
            parent_id     = None if parent_id_str == 'null' else int(parent_id_str)
        except ValueError:
            raise MethodException("parent_id must be an int or 'null'")

        groups = handler.facade_manager.get_groups(session_id, parent_id)
        return { 'response' :
                    { 'data' :
                        [
                            {
                                'id' : group.id,
                                'name' : group.name,
                                'parent_id' : None if group._parent is None else group._parent.id,
                                'isFolder'  : len(group.children) > 0
                            }
                            for group in groups
                        ]
                    }
                }

    @staticmethod
    def get_experiment_uses(handler, session_id, parameters):
        advanced_criteria = AdvancedCriteria.parse(parameters)

        session_id    = { 'id' : session_id }

        if 'start_date' in advanced_criteria.criterias:
            from_date     = advanced_criteria.criterias['start_date'].value
        else:
            from_date     = None
        if 'end_date' in advanced_criteria.criterias:
            to_date       = advanced_criteria.criterias['end_date'].value
        else:
            to_date       = None
        if 'group' in advanced_criteria.criterias:
            group_id      = advanced_criteria.criterias['group'].value
        else:
            group_id      = None
        if 'experiment_id' in advanced_criteria.criterias:
            experiment_id = advanced_criteria.criterias['experiment_id'].value
        else:
            experiment_id = None

        start_row     = advanced_criteria.start_row
        end_row       = advanced_criteria.end_row
        sort_by       = advanced_criteria.sort_by

        experiment_uses, total_rows = handler.facade_manager.get_experiment_uses(session_id, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by)

        return {
                'response' : {
                    'status'    : 0,
                    'startRows' : start_row,
                    'endRow'    : start_row + len(experiment_uses),
                    'totalRows' : total_rows,
                    'data' : [
                        {
                            'id'                  : experiment_use.id,
                            'start_date'          : experiment_use.start_date.strftime(Criteria.DATETIME_FORMAT) if experiment_use.start_date is not None else None,
                            'end_date'            : experiment_use.end_date.strftime(Criteria.DATETIME_FORMAT) if experiment_use.end_date is not None else None,
                            'agent_login'         : experiment_use.agent.login,
                            'agent_name'          : experiment_use.agent.full_name,
                            'agent_email'         : experiment_use.agent.email,
                            'experiment_name'     : experiment_use.experiment.name,
                            'experiment_category' : experiment_use.experiment.category.name,
                            'origin'              : experiment_use.origin
                        } for experiment_use in experiment_uses
                    ]
                }
            }


class SmartGwtHttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    facade_manager = None
    server_route   = None

    def do_GET(self):
        create_context(self.server, self.client_address, self.headers)
        try:
            first_question_mark = self.path.find("?")
            if first_question_mark >= 0:
                path = self.path[0:first_question_mark]
                options = urllib.unquote(self.path[first_question_mark + 1:])
            else:
                path = self.path
                options = ""

            parameters = [ field for field in options.split("&") if field.find("=") >= 0 ]

            session_id_param = [ field[field.find("=") + 1:] for field in parameters if field.startswith("sessionid") ]
            if len(session_id_param) == 0:
                self._write(400, "sessionid not provided")
                return

            session_id = session_id_param[0]

            last_slash = path.rfind("/")
            if last_slash >= 0:
                method_name = path[last_slash + 1:]
            else:
                method_name = path

            if 'get_%s' % method_name in dir(Methods):
                method = getattr(Methods, 'get_%s' % method_name)
                try:
                    response = method(self, session_id, parameters)
                except MethodException as me:
#                    import traceback
#                    traceback.print_exc()
                    log.log( self, log.level.Error, str(me))
                    log.log_exc( self, log.level.Warning)
                    self._write(400, "Error: %s" % me)
                    return
                json_response = json.dumps(response)
            else:
                self._write(400, "method %s not implemented" % urllib2.quote(method_name))
                return

            self._write(200, json_response)
        except Exception as e:
            import traceback
            traceback.print_exc()

            log.log( self, log.level.Error, str(e))
            log.log_exc( self, log.level.Warning)
            self._write(500, 'Error in server. Contact administrator')
        finally:
            delete_context()

    def _write(self, code, response):
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)
        self.wfile.flush()
        try:
            self.connection.shutdown(1)
        except:
            pass

    def do_OPTIONS(self):
        return self.do_GET()

    def log_message(self, format, *args):
        #args: ('POST /foo/bar/ HTTP/1.1', '200', '-')
        log.log(
            SmartGwtHttpHandler,
            log.level.Info,
            "Request from %s: %s" % (get_context().get_ip_address(), format % args)
        )

class AdminFacadeServerSmartGWT(RemoteFacadeServerJSON):
    protocol_name = 'smartgwt'
    JSON_HANDLER  = SmartGwtHttpHandler
