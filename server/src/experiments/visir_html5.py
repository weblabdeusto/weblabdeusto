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
import httplib
import urllib2
import urllib
import threading
import traceback
import time
import random
import xml.dom.minidom as xml
import json

from voodoo.log import logged
from voodoo.override import Override

import voodoo.sessions.manager as SessionManager
import voodoo.sessions.session_type as SessionType
from voodoo.sessions.exc import SessionNotFoundError
from voodoo.typechecker import typecheck, ANY

CFG_USE_VISIR_PHP = "vt_use_visir_php"

CFG_MEASURE_SERVER_ADDRESS = "vt_measure_server_addr"
CFG_MEASURE_SERVER_TARGET = "vt_measure_server_target"
CFG_LOGIN_URL = "vt_login_url"
CFG_BASE_URL = "vt_base_url"
CFG_LOGIN_EMAIL = "vt_login_email"
CFG_LOGIN_PASSWORD = "vt_login_password"
CFG_SAVEDATA = "vt_savedata"
CFG_TEACHER  = "vt_teacher"
CFG_CLIENT_URL = "vt_client_url"
CFG_HEARTBEAT_PERIOD = "vt_heartbeat_period"
CFG_CIRCUITS = "vt_circuits"
CFG_CIRCUITS_DIR = "vt_circuits_dir"
CFG_DEBUG_PRINTS = "vt_debug_prints"
CFG_LIBRARY_XML  = "vt_library"
CFG_OSCILLOSCOPE_RUNNABLE = "vt_oscilloscope_runnable"
CFG_OSCILLOSCOPE_COUNT = "vt_oscilloscope_count"

DEFAULT_USE_VISIR_PHP = True
DEFAULT_MEASURE_SERVER_ADDRESS = "130.206.138.35:8080"
DEFAULT_MEASURE_SERVER_TARGET = "/measureserver"
DEFAULT_LOGIN_URL = """https://weblab-visir.deusto.es/electronics/student.php"""
DEFAULT_BASE_URL = """https://weblab-visir.deusto.es/"""
DEFAULT_LOGIN_EMAIL = "guest"
DEFAULT_LOGIN_PASSWORD = "guest"
DEFAULT_SAVEDATA = ""
DEFAULT_TEACHER  = True
DEFAULT_CLIENT_URL = "../web/visir/loader.swf"
DEFAULT_HEARTBEAT_PERIOD = 30
DEFAULT_CIRCUITS = {}
DEFAULT_DEBUG_PRINTS = False


HEARTBEAT_REQUEST = """<protocol version="1.3"><request sessionkey="%s"/></protocol>"""
HEARTBEAT_MAX_SLEEP = 5

# Actually defined through the configuration.
DEBUG = None

class Heartbeater(threading.Thread):
    """
    The Heartbeater is a different thread, which will periodically send a heartbeat
    request if no other requests have been sent recently.
    """

    @typecheck(ANY, basestring, int, basestring, SessionManager.SessionManager)
    def __init__(self, experiment, heartbeat_period, session_manager):
        """
        Creates the Heartbeater object. The Heartbeater is a thread which will periodically
        send requests as heartbeats (because actual heartbeat or even login requests do not work).

        There should be a single Heartbeater, which will send the periodical requests to every
        user that needs so.

        The heartbeat may be inhibited through periodical tick() calls.

        For the Heartbeater to start working, it needs to be started through start(). To stop it,
        stop() must be called. It is noteworthy that stop is not immediate.

        Every heartbeat will be carried out from the same thread, sequentially. Hence, especially
        with a high number of users, it may theoretically take a long time to send a specific
        heartbeat. This should not be an issue unless the heartbeat frequency is set too low.

        @param experiment Reference to the VisirTestExperiment. Will make use of the user map within it.
        @param heartbeat_period Number of seconds between heartbeats.
        @param session_manager The session manager from which retrieve the sessions

        @see start
        @see stop
        @see tick
        """
        threading.Thread.__init__(self)
        self.is_stopped = False
        self.experiment = experiment
        self.heartbeat_period = heartbeat_period
        self.session_manager  = session_manager

    def stop(self):
        """
        Stops the thread. The thread is not stopped immediately. Instead, a flag is
        internally set and the actual thread will finish when possible.
        Once called, stopped() will return true (without waiting for the thread to
        actually finish).

        @see stopped
        """
        self.is_stopped = True

    def stopped(self):
        """
        Returns true if the thread has been explicitly stopped. False otherwise.
        Note that before the thread has been started, stopped will still be false.
        That is, it will start returning true just as soon as stop is called.

        @see stop
        @see is_alive
        """
        return self.is_stopped

    def tick(self, session_object):
        """
        tick()
        Ticks to update the time for a given session. If the session has not been registered
        the tick operation does nothing.

        @param lab_session_id Session id of the user counter to tick
        Should be called, both internally or externally, whenever a heartbeat or any
        other packet is sent to reset OR INITIALIZE the heartbeat timer.
        """

        # If the session id is not registered within the sessions map, we will simply
        # return without doing anything. This can happen for the initial login request.
        session_object['last_heartbeat_sent'] = time.time()
        if DEBUG: print "[DBG] HB TICK"


    def run(self):
        """
        run()

        Thread process. Thread starts running here when start() is called.
        @see start
        """

        if DEBUG: dbg("[DBG] HB INIT")

        while(True):
            if self.stopped():
                return
            try:
                # Sleep at most HEARTBEAT_MAX_SLEEP. We will most likely overwrite this
                # with a lower value, depending on the pending requests.
                time_to_sleep = HEARTBEAT_MAX_SLEEP

                # Loop through every user that is using the experiment concurrently, and consider
                # whether we should update it or not.
                if DEBUG_HEARTBEAT_MESSAGES: print "[DBG] HB Listing sessions..."

                for session_id in self.session_manager.list_sessions():
                    if DEBUG_HEARTBEAT_MESSAGES: print "[DBG] HB checking session_id=%s" % (session_id)
                    try:
                        sessiondata = self.session_manager.get_session_locking(session_id)
                    except SessionNotFoundError:
                        if DEBUG_HEARTBEAT_MESSAGES: print "[DBG] HB no session found for session_id=%s" % (session_id)
                        continue


                    if 'sessionkey' not in sessiondata:
                        self.session_manager.modify_session_unlocking(session_id, sessiondata)
                        if DEBUG_HEARTBEAT_MESSAGES: print "[DBG] HB no sessionkey found in sessiondata for session_id=%s" % (session_id)
                        continue

                    try:

                        # Evaluate the time left for the next potential heartbeat.
                        if 'last_heartbeat_sent' not in sessiondata:
                            # If we actually don't have a last_heartbeat_sent yet,
                            # initialize it.
                            sessiondata['last_heartbeat_sent'] = time.time()
                        last_sent = sessiondata['last_heartbeat_sent']
                        session_key = sessiondata['sessionkey']
                    finally:
                        self.session_manager.modify_session_unlocking(session_id, sessiondata)

                    time_left = (last_sent + self.heartbeat_period) - time.time()

                    # If time_left is zero or negative, a heartbeat IS due.
                    if(time_left <= 0):
                        if DEBUG_HEARTBEAT_MESSAGES: dbg("[DBG] HB FORWARDING")
                        ret = self.experiment.forward_request(session_id, HEARTBEAT_REQUEST % (session_key))
                        if DEBUG_HEARTBEAT_MESSAGES: dbg("[DBG] Heartbeat response: %s" % ret)

                    else:
                        # Otherwise, we will just sleep.
                        if DEBUG_HEARTBEAT_MESSAGES: print "[DBG] HB SLEEPING FOR %d" % (time_left)

                        # We wish to sleep the maximum only if there are no pending
                        # requests (and if it doesn't go over the MAX).
                        time_to_sleep = min(time_left, time_to_sleep)

                if DEBUG_HEARTBEAT_MESSAGES: print "[DBG] Listing sessions finished"
                sys.stdout.flush()

                # We will actually not sleep the whole time_to_sleep at once, so that
                # we can check whether the thread has finished more often.
                # TODO: Consider doing this through semaphores so that we do not need
                # this work-around.
                step_time = 0.1
                steps = time_to_sleep / step_time
                while not self.stopped() and steps > 0:
                    time.sleep(step_time)
                    steps -= 1
                if DEBUG_HEARTBEAT_MESSAGES: print "[DBG] Not sleeping anymore"
                sys.stdout.flush()

            except:
                # TODO: use log
                traceback.print_exc()
                time.sleep(5)

DEBUG_MESSAGES = DEBUG
DEBUG_HEARTBEAT_MESSAGES = DEBUG_MESSAGES

def dbg(message):
    print message
    sys.stdout.flush()

class VisirExperiment(ConcurrentExperiment.ConcurrentExperiment):

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(VisirExperiment, self).__init__(*args, **kwargs)
        self._cfg_manager = cfg_manager
        self.read_config()
        self._requesting_lock = threading.Lock()

        # We will initialize and start it later
        self.heartbeater = None
        self.heartbeater_lock = threading.Lock()
        self._users_counter_lock = threading.Lock()
        self.users_counter = 0

        # XXX It must be SessionType.Memory, since we are storing an HTTPConnection object
        self._session_manager = SessionManager.SessionManager( cfg_manager, SessionType.Memory, "visir" )

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
        self.heartbeat_period = self._cfg_manager.get_value(CFG_HEARTBEAT_PERIOD, DEFAULT_HEARTBEAT_PERIOD)
        self.circuits     = self._cfg_manager.get_value(CFG_CIRCUITS, DEFAULT_CIRCUITS)
        self.circuits_dir = self._cfg_manager.get_value(CFG_CIRCUITS_DIR, None)
        self.library_xml  = self._cfg_manager.get_value(CFG_LIBRARY_XML, "failed")
        self.oscilloscope_count = self._cfg_manager.get_value(CFG_OSCILLOSCOPE_COUNT, None)
        self.oscilloscope_runnable = self._cfg_manager.get_value(CFG_OSCILLOSCOPE_RUNNABLE, None)

        global DEBUG
        DEBUG = self._cfg_manager.get_value(CFG_DEBUG_PRINTS, DEFAULT_DEBUG_PRINTS)

        #
        # There are two ways of deploying VISIR:
        # - with all the OpenLabs Web code
        # - directly without authentication against the measurement server
        #
        # We support both, depending on this variable.
        #
        self.use_visir_php = self._cfg_manager.get_value(CFG_USE_VISIR_PHP, DEFAULT_USE_VISIR_PHP)

        if self.use_visir_php:
            self.loginurl       = self._cfg_manager.get_value(CFG_LOGIN_URL, DEFAULT_LOGIN_URL)
            self.basephpurl     = self._cfg_manager.get_value(CFG_BASE_URL, DEFAULT_BASE_URL)
            self.login_email    = self._cfg_manager.get_value(CFG_LOGIN_EMAIL, DEFAULT_LOGIN_EMAIL)
            self.login_password = self._cfg_manager.get_value(CFG_LOGIN_PASSWORD, DEFAULT_LOGIN_PASSWORD)

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

        # Consider whether we should initialize the heartbeater now. If we are the first
        # user, the heartbeater will not have started yet.
        with self.heartbeater_lock:
            if self.heartbeater is None:
                self.heartbeater = Heartbeater(self, self.heartbeat_period, self._session_manager)
                self.heartbeater.setDaemon(True)
                self.heartbeater.setName('Heartbeater')
                self.heartbeater.start()

        if DEBUG: dbg("[DBG] Current number of users: %s" % len(self._session_manager.list_sessions()))
        if DEBUG: dbg("[DBG] Lab Session Id: %s" % lab_session_id)
        if DEBUG: dbg("[DBG] Measure server address: %s" % self.measure_server_addr)
        if DEBUG: dbg("[DBG] Measure server target: %s" % self.measure_server_target)

        try:
            initial_data = json.loads(client_initial_data or '{}')
        except:
            initial_data = {}

        if 'savedata' in initial_data:
            savedata = initial_data['savedata']
        else:
            savedata = None

        setup_data = self.build_setup_data("", self.client_url, self.get_circuits().keys(), savedata)

        self._session_manager.create_session(lab_session_id.id)
        self._session_manager.modify_session(lab_session_id, {'cookie' : "", 'electro_lab_cookie' : ""})

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
            data = self.forward_request(lab_session_id, "<protocol version=\"1.3\"><login keepalive=\"1\"/></protocol>")
            session_key = self.extract_sessionkey(data)
            user = self._session_manager.get_session_locking(lab_session_id)
            try:
                # Store the session for the user
                user['sessionkey'] = session_key
                if DEBUG: dbg("[DBG] Extracted sessionkey: " + user['sessionkey'])
            finally:
                self._session_manager.modify_session_unlocking(lab_session_id, user)

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

            data = self.forward_request(lab_session_id, command)

            dom = xml.parseString(data)
            multimeter = dom.getElementsByTagName('multimeter')
            for i in range(0, len(multimeter)):
                multimeter[i].setAttribute("id", str(i+1))

            data = dom.toxml().replace("<?xml version=\"1.0\" ?>", "")

            if DEBUG_MESSAGES:
                dbg("[DBG] DATA: "+data)

        return data

    def extract_sessionkey(self, command):
        """
        Extracts the sessionkey from the response to a <login> request.
        @param command The request, in a string containing the raw XML of the response.
        """
        dom = xml.parseString(command)
        protocol_node = dom.firstChild

        # Find the next non-text node.
        for n in protocol_node.childNodes:
            if n.nodeName != "#text":
                login_node = n

        sessionkey = login_node.getAttribute("sessionkey")

        return sessionkey


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

    def build_setup_data(self, cookie, url, circuits_list, client_savedata):
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

        session_obj = self._session_manager.get_session_locking(lab_session_id)
        try:
            if 'connection' in session_obj:
                conn = session_obj['connection']
            else:
                conn = httplib.HTTPConnection(self.measure_server_addr)
                session_obj['connection'] = conn

            conn.request("POST", self.measure_server_target, request)
            response = conn.getresponse()
            data = response.read()
            response.close()

            # We just sent a request. Tick the heartbeater.
            self.heartbeater.tick(session_obj)
        finally:
            self._session_manager.modify_session_unlocking(lab_session_id, session_obj)

        if DEBUG_MESSAGES:
            dbg("[VisirTestExperiment] Received response: %s" % data)

        return data

    def perform_visir_web_login(self, url, email, password):
        """
        Performs a login through the specified visir web url.
        @param url Url to the file through which to login. May contain
        GET parameters if required.
        @param email Email or account name to use
        @param password Password to use
        @return The cookie that was returned upon a successful login, and
        None upon a failed one
        """

        # Create the POST data with the parameters
        postvals = {"email" : email,
                    "password" : password }
        postdata = urllib.urlencode(postvals)

        # We need to use a Cookie processor to be able to retrieve
        # the auth cookie that we seek

        cp = urllib2.HTTPCookieProcessor()
        o = urllib2.build_opener( cp )
        #urllib2.install_opener(o)

        # Do the sel=login request. This request should yield a electro_lab cookie,
        # and if successful a logout link will be provided in the answer.
        r = o.open(url, postdata)
        content = r.read()
        if content.find('sel=logout') >= 0:
            if DEBUG: print "Found Logout link"
        else:
            print "WARNING: logout link not found!!!"
        r.close()

        # Do a sel=occasion query. This is most likely not necessary, but included
        # here to mirror the standard procedure as closely as possible.
        r = o.open("%s/experiment.php?sel=occasion&id=2" % self.basephpurl)
        r.read()
        r.close()

        # Do a sel=experiment_immediate query. This is the last query before the experiment
        # starts. It yields an exp_session query.
        r = o.open("%s/experiment.php?sel=experiment_immediate&id=2&http=1" % self.basephpurl)
        r.read()
        r.close()

        # Extract both relevant cookies; electro_lab and exp_session.
        cookies = dict(( (c.name, c.value) for c in cp.cookiejar ))

        if 'electro_lab' not in cookies:
            print "WARNING: could not find electro_lab cookie!!!"
            sys.stdout.flush()
        if 'exp_session' not in cookies:
            print "WARNING: could not find exp_session cookie!!!"
            sys.stdout.flush()

        electro_lab_cookie = cookies.get('electro_lab','')
        exp_session_cookie = cookies.get('exp_session','any_exp_session_%s' % random.random())

        if DEBUG: print "[DBG] LOGIN DONE. ELECTRO_LAB = %s AND EXP_SESSION = %s" % (electro_lab_cookie, exp_session_cookie)

        return electro_lab_cookie, exp_session_cookie



    @Override(ConcurrentExperiment.ConcurrentExperiment)
    @logged()
    def do_send_file_to_device(self, lab_session_id, content, file_info):
        """
        Callback for when the client sends a file to the experiment
        server. Currently unused for this experiment, should never get
        called.
        """
        if DEBUG: print "[DBG] Lab Session Id: ", lab_session_id
        if(DEBUG):
            print "[VisirTestExperiment] do_send_file_to_device called"
        return "Ok"


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


        sess_obj = self._session_manager.get_session(lab_session_id)
        if 'connection' in sess_obj:
            try:
                sess_obj['connection'].close()
            except:
                traceback.print_exc()
        self._session_manager.delete_session(lab_session_id)
        with self.heartbeater_lock:
            users_left = len(self._session_manager.list_sessions()) != 0

            if not users_left:
                if DEBUG: print "[DBG] No users left. Stopping heartbeater thread."

                heartbeater = self.heartbeater
                self.heartbeater = None

        if not users_left:
            if heartbeater is not None: # Not removed in other thread
                heartbeater.stop()
                heartbeater.join(60)

                if heartbeater.is_alive():
                    raise Exception("[ERROR/Visir] The heartbeater thread could not be stopped in time")

            if DEBUG: print "[DBG] Heartbeater thread successfully stopped."

        if DEBUG: print "[DBG] Finished successfully: ", lab_session_id

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
