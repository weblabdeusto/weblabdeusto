#!/usr/bin/python
# -*- coding: utf-8 -*-
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
# Author: Luis Rodríguez <luis.rodriguez@opendeusto.es>
#         Pablo Orduña <pablo@ordunya.com>
#

import weblab.experiment.concurrent_experiment as ConcurrentExperiment

import os
import sys
import glob
import urllib
import hashlib
import threading
import traceback
import time
import random
import xml.dom.minidom as xml
import json

import requests

from voodoo.log import logged
from voodoo.override import Override

import voodoo.sessions.manager as SessionManager
import voodoo.sessions.session_type as SessionType
from voodoo.sessions.exc import SessionNotFoundError
from voodoo.typechecker import typecheck, ANY

CFG_MEASURE_SERVER_ADDRESS = "vt_measure_server_addr"
CFG_MEASURE_SERVER_TARGET = "vt_measure_server_target"
CFG_SAVEDATA = "vt_savedata"
CFG_TEACHER  = "vt_teacher"
CFG_CLIENT_URL = "vt_client_url"
CFG_CIRCUITS = "vt_circuits"
CFG_CIRCUITS_DIR = "vt_circuits_dir"
CFG_DEBUG_PRINTS = "vt_debug_prints"
CFG_LIBRARY_XML  = "vt_library"
CFG_OSCILLOSCOPE_RUNNABLE = "vt_oscilloscope_runnable"
CFG_OSCILLOSCOPE_COUNT = "vt_oscilloscope_count"

DEFAULT_MEASURE_SERVER_ADDRESS = "130.206.138.35:8080"
DEFAULT_MEASURE_SERVER_TARGET = "/measureserver"
DEFAULT_LOGIN_URL = """https://weblab-visir.deusto.es/electronics/student.php"""
DEFAULT_BASE_URL = """https://weblab-visir.deusto.es/"""
DEFAULT_LOGIN_EMAIL = "guest"
DEFAULT_LOGIN_PASSWORD = "guest"
DEFAULT_SAVEDATA = ""
DEFAULT_TEACHER  = True
DEFAULT_CLIENT_URL = "../web/visir/loader.swf"
DEFAULT_CIRCUITS = {}
DEFAULT_DEBUG_PRINTS = False

# Actually defined through the configuration.
DEBUG = None
DEBUG_MESSAGES = DEBUG

def dbg(message):
    print message
    sys.stdout.flush()

class VisirExperiment(ConcurrentExperiment.ConcurrentExperiment):

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(VisirExperiment, self).__init__(*args, **kwargs)
        self._cfg_manager = cfg_manager
        self.read_config()
        self._requesting_lock = threading.Lock()
        self._requests_session = {}

        self._users_counter_lock = threading.Lock()
        self.users_counter = 0

    @Override(ConcurrentExperiment.ConcurrentExperiment)
    def do_get_api(self):
        return "2_concurrent"

    def read_config(self):
        """
        Reads the config parameters from the config file (such as the
        measurement server address)
        """

        # Common configuration values
        self.savedata   = self._cfg_manager.get_value(CFG_SAVEDATA, DEFAULT_SAVEDATA)
        self.teacher    = self._cfg_manager.get_value(CFG_TEACHER, DEFAULT_TEACHER)
        self.client_url = self._cfg_manager.get_value(CFG_CLIENT_URL, DEFAULT_CLIENT_URL)
        self.measure_server_addr = self._cfg_manager.get_value(CFG_MEASURE_SERVER_ADDRESS, DEFAULT_MEASURE_SERVER_ADDRESS)
        self.measure_server_target = self._cfg_manager.get_value(CFG_MEASURE_SERVER_TARGET, DEFAULT_MEASURE_SERVER_TARGET)
        self.circuits     = self._cfg_manager.get_value(CFG_CIRCUITS, DEFAULT_CIRCUITS)
        self.circuits_dir = self._cfg_manager.get_value(CFG_CIRCUITS_DIR, None)
        self.library_xml  = self._cfg_manager.get_value(CFG_LIBRARY_XML, "failed")
        self.oscilloscope_count = self._cfg_manager.get_value(CFG_OSCILLOSCOPE_COUNT, None)
        self.oscilloscope_runnable = self._cfg_manager.get_value(CFG_OSCILLOSCOPE_RUNNABLE, None)

        global DEBUG
        DEBUG = self._cfg_manager.get_value(CFG_DEBUG_PRINTS, DEFAULT_DEBUG_PRINTS)

    def get_circuits(self):
        all_circuits = self.circuits.copy()
        try:
            if self.circuits_dir is not None:
                for fname in glob.glob("%s*cir" % self.circuits_dir):
                    name = os.path.basename(fname)[:-4]
                    all_circuits[name] = urllib.quote(open(fname, "rb").read(), '')
        except:
            traceback.print_exc()
        return all_circuits

    @Override(ConcurrentExperiment.ConcurrentExperiment)
    @logged()
    def do_start_experiment(self, lab_session_id, client_initial_data, server_initial_data):
        """
        Callback run when the experiment is started
        """

        if DEBUG: dbg("[DBG] Lab Session Id: %s" % lab_session_id)
        if DEBUG: dbg("[DBG] Measure server address: %s" % self.measure_server_addr)
        if DEBUG: dbg("[DBG] Measure server target: %s" % self.measure_server_target)

        try:
            initial_data = json.loads(client_initial_data or '{}')
        except:
            initial_data = {}

        self._requests_session[lab_session_id] = requests.Session()

        if 'savedata' in initial_data:
            savedata = initial_data['savedata']
        else:
            savedata = None

        setup_data = self.build_setup_data("", self.client_url, self.get_circuits().keys(), savedata, initial_data)

        # Increment the user's counter, which indicates how many users are using the experiment.
        with self._users_counter_lock:
            self.users_counter += 1

        if(DEBUG): dbg("[VisirTestExperiment][Start]: Current users: %s" % self.users_counter)

        return json.dumps({ "initial_configuration" : setup_data, "batch" : False })

    @Override(ConcurrentExperiment.ConcurrentExperiment)
    @logged()
    def do_send_command_to_device(self, lab_session_id, command):
        """
        Callback run when the client sends a command to the experiment
        @param command Command sent by the client, as a string.
        """

        if DEBUG: dbg("[DBG] Lab Session Id: %s" % lab_session_id)

        data = ""

        # This command is currently not used.
        if command == "GIVE_ME_CIRCUIT_LIST":
            circuit_list = self.get_circuits().keys()
            circuit_list_string = ""
            for c in circuit_list:
                circuit_list_string += c
                circuit_list_string += ','
            return circuit_list_string

        elif command.startswith("GIVE_ME_CIRCUIT_DATA"):
            print "[DBG] GOT GIVE_ME_CIRCUIT_DATA_REQUEST"
            circuit_name = command.split(' ', 1)[1]
            circuit_data = self.get_circuits()[circuit_name]
            return circuit_data
        elif command == 'GIVE_ME_LIBRARY':
            if DEBUG: dbg("[DBG] GOT GIVE_ME_LIBRARY")
            return self.library_xml

        elif command == "login":
            if DEBUG: dbg("[DBG] LOGIN")
            session_key = hashlib.md5('{}-{}'.format(time.time(), random.random())).hexdigest()
            data = json.dumps({"teacher": self.teacher, "sessionkey": session_key})
        elif command.startswith("load"):
            if DEBUG: dbg("Circuit loaded: " + command[5:])
            
            try:
                circuit = xml.parseString(command[5:])
            except:
                traceback.print_exc()

        elif command.startswith("save"):
            if DEBUG: dbg("Circuit saved: " + command[5:])
    
            try:
                circuit = xml.parseString(command[5:])
            except:
                traceback.print_exc()
        else:
            if DEBUG:
                dbg("[DBG] REQUEST TYPE: " + self.parse_request_type(command))
                dbg("[DBG] SESSION ID: %s" % lab_session_id)

            try:
                dom = xml.parseString(command)
                protocol_nodes = dom.getElementsByTagName('protocol')
                if protocol_nodes:
                    save_nodes = protocol_nodes[0].getElementsByTagName('save')
                    if save_nodes:
                        for save_node in save_nodes:
                            save_node.parentNode.removeChild(save_node)

                        command = protocol_nodes[0].toxml().replace("<?xml version=\"1.0\" ?>", "")
            except:
                pass

            data = self.forward_request(lab_session_id, command)

            dom = xml.parseString(data)
            multimeter = dom.getElementsByTagName('multimeter')
            for i in range(0, len(multimeter)):
                multimeter[i].setAttribute("id", str(i+1))

            data = dom.toxml().replace("<?xml version=\"1.0\" ?>", "")

            if DEBUG_MESSAGES:
                dbg("[DBG] DATA: "+data)

        return data

    def parse_request_type(self, command):
        """
        Will obtain the request type. That is, the name of the node beneath the root <protocol> node.
        @param command (String) The raw XML request or response.
        """
        dom = xml.parseString(command)
        protocol_node = dom.firstChild

        # Find the next non-text node.
        for n in protocol_node.childNodes:
            if n.nodeName != "#text":
                return n.nodeName

    def build_setup_data(self, cookie, url, circuits_list, client_savedata, initial_data):
        """
        Helper function that will return a structure with the initialization data,
        json-encoded in a string.

        @param cookie Visir cookie for the session.
        @param url URL for the client to find the visir files.
        @param circuits_list List of the names of the circuits that are available.
        """
        data = {
                "cookie"   : cookie,
                "savedata" : urllib.quote(client_savedata or self.savedata, ''),
                "url"      : url,
                "teacher"  : self.teacher,
                "experiments" : self.teacher,
                "circuits" : circuits_list,
            }
        for key in ['dcPower25', 'dcPowerM25', 'dcPower6']:
            if key in initial_data:
                data[key] = initial_data[key]

        # if self.library_xml and self.library_xml != 'failed' and self.library_xml != 'fail':
        #     data['libraryXml'] = self.library_xml

        if self.oscilloscope_count:
            data['oscilloscopeCount'] = self.oscilloscope_count

        if self.oscilloscope_runnable:
            data['oscilloscopeRunnable'] = self.oscilloscope_runnable

        return json.dumps(data)

    def forward_request(self, lab_session_id, request):
        """
        Forwards a request to the VISIR Measurement Server through an
        HTTP POST.
        @param request String containing the request to be forwarded
        """
        if DEBUG_MESSAGES:
            dbg("[VisirTestExperiment] Forwarding request to %s: %s" % (self.measure_server_addr, request))

        rsession = self._requests_session.get(lab_session_id)
        if rsession is None:
            rsession = requests.Session()

        url = 'http://{}{}'.format(self.measure_server_addr, self.measure_server_target)
        result = rsession.post(url, data=request, timeout=(300, 300))
        data = result.content

        if DEBUG_MESSAGES:
            dbg("[VisirTestExperiment] Received response: %s" % data)

        return data

    @Override(ConcurrentExperiment.ConcurrentExperiment)
    @logged()
    def do_dispose(self, lab_session_id):
        """
        Callback to perform cleaning after the experiment ends.
        """

        if DEBUG: print "[DBG] Lab Session Id: ", lab_session_id
        if(DEBUG):
            print "[VisirTestExperiment] do_dispose called"

        if(DEBUG): print "[VisirTestExperiment][Dispose]: Current users: ", self.users_counter

        # Decrease the users counter
        with self._users_counter_lock:
            self.users_counter -= 1

        if DEBUG: print "[DBG] Finished successfully: ", lab_session_id
        self._requests_session.pop(lab_session_id, None)

        return "ok"

# Backwards compatible...
VisirTestExperiment = VisirExperiment

if __name__ == '__main__':
    regular_request = """<protocol version="1.3"><request sessionkey="%s"><circuit><circuitlist>W_X VDC+6V_1_1 A6
W_X A10 IPROBE_1_1
W_X IPROBE_1_2 0
R_X A6 A10 1k
IPROBE_1 IPROBE_1_1 IPROBE_1_2
VDC+6V_1 VDC+6V_1_1
</circuitlist></circuit><multimeter id="1"><dmm_function value="dc current"></dmm_function><dmm_resolution value="3.5"></dmm_resolution><dmm_range value="-1"></dmm_range><dmm_autozero value="1"></dmm_autozero></multimeter><functiongenerator id="1"><fg_waveform value="sine"></fg_waveform><fg_frequency value="1000"></fg_frequency><fg_amplitude value="0.5"></fg_amplitude><fg_offset value="0"></fg_offset></functiongenerator><oscilloscope id="1"><horizontal><horz_samplerate value="500"></horz_samplerate><horz_refpos value="50"></horz_refpos><horz_recordlength value="500"></horz_recordlength></horizontal><channels><channel number="1"><chan_enabled value="1"></chan_enabled><chan_coupling value="dc"></chan_coupling><chan_range value="1"></chan_range><chan_offset value="0"></chan_offset><chan_attenuation value="1"></chan_attenuation></channel><channel number="2"><chan_enabled value="1"></chan_enabled><chan_coupling value="dc"></chan_coupling><chan_range value="1"></chan_range><chan_offset value="0"></chan_offset><chan_attenuation value="1"></chan_attenuation></channel></channels><trigger><trig_source value="channel 1"></trig_source><trig_slope value="positive"></trig_slope><trig_coupling value="dc"></trig_coupling><trig_level value="0"></trig_level><trig_mode value="autolevel"></trig_mode><trig_timeout value="1"></trig_timeout><trig_delay value="0"></trig_delay></trigger><measurements><measurement number="1"><meas_channel value="channel 1"></meas_channel><meas_selection value="none"></meas_selection></measurement><measurement number="2"><meas_channel value="channel 1"></meas_channel><meas_selection value="none"></meas_selection></measurement><measurement number="3"><meas_channel value="channel 1"></meas_channel><meas_selection value="none"></meas_selection></measurement></measurements><osc_autoscale value="0"></osc_autoscale></oscilloscope><dcpower id="1"><dc_outputs><dc_output channel="6V+"><dc_voltage value="2.5"></dc_voltage><dc_current value="0.5"></dc_current></dc_output><dc_output channel="25V+"><dc_voltage value="0"></dc_voltage><dc_current value="0.5"></dc_current></dc_output><dc_output channel="25V-"><dc_voltage value="0"></dc_voltage><dc_current value="0.5"></dc_current></dc_output></dc_outputs></dcpower></request></protocol>"""
    from voodoo.configuration import ConfigurationManager
    from voodoo.sessions.session_id import SessionId
    cfg_manager = ConfigurationManager()
    try:
        cfg_manager.append_path("../../launch/sample/main_machine/main_instance/experiment_testvisir/server_config.py")
    except:
        cfg_manager.append_path("../launch/sample/main_machine/main_instance/experiment_testvisir/server_config.py")

    experiment = VisirExperiment(None, None, cfg_manager)
    lab_session_id = SessionId('sess1')
    experiment.do_start_experiment(lab_session_id)

    login_response = json.loads(experiment.do_send_command_to_device(lab_session_id, "login"))
    sessionkey = login_response['sessionkey']
    request = regular_request % sessionkey
    experiment.do_send_command_to_device(lab_session_id, request)

    time.sleep(1)

    lab_session_id2 = SessionId('sess2')
    experiment.do_start_experiment(lab_session_id2)

    login_response2 = json.loads(experiment.do_send_command_to_device(lab_session_id2, "login"))
    sessionkey2 = login_response2['sessionkey']
    request2 = regular_request % sessionkey2
    experiment.do_send_command_to_device(lab_session_id2, request2)

    time.sleep(1)

    lab_session_id3 = SessionId('sess3')
    experiment.do_start_experiment(lab_session_id3)

    login_response3 = json.loads(experiment.do_send_command_to_device(lab_session_id3, "login"))
    sessionkey3 = login_response3['sessionkey']
    request3 = regular_request % sessionkey3
    experiment.do_send_command_to_device(lab_session_id3, request3)

    time.sleep(5)
