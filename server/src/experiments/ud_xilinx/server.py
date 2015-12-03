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
# Author: Pablo Orduña <pablo@ordunya.com>
#         Jaime Irurzun <jaime.irurzun@gmail.com>
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
#

import os
import tempfile
import urllib2
import json
import base64
import time
import random
import traceback

from voodoo.gen.caller_checker import caller_check
from voodoo.log import logged
from voodoo.override import Override
from experiments.ud_xilinx.command_senders import UdXilinxCommandSender
from weblab.experiment.devices.xilinx.programmers.programmers import XilinxProgrammer
import voodoo.log as log
import weblab.data.server_type as ServerType
import weblab.experiment.exc as ExperimentErrors
import weblab.experiment.experiment as Experiment
import weblab.experiment.util as ExperimentUtil
from experiments.xilinxc.compiler import Compiler
import watertank_simulation
from voodoo.threaded import threaded

"""
Notes on the LEDS & SWITCHES

There are 10 switches and 8 leds, though queryLeds returns more.
The leds list goes from left to right. leds_list[0] is thus led7 and leds_list[7] is led0

In the hardware (UCF file) led0 is the rightmost, and swi0 is also the rightmost.

For the board, however, the rightmost switch is switch 9, while the leftmost is 0 (the client thus reverses
the numbers)

The led states list
"""




# Though it would be slightly more efficient to use single characters, it's a text protocol
# after all, so we will use words for readability.
STATE_NOT_READY = "not_ready"
STATE_AWAITING_CODE = "awaiting_code"
STATE_SYNTHESIZING = "synthesizing"
STATE_SYNTHESIZING_ERROR = "synthesizing_error"
STATE_PROGRAMMING = "programming"
STATE_READY = "ready"
STATE_FAILED = "failed"
STATE_NOT_ALLOWED = "not_allowed"
STATE_USE_TIME_EXCEEDED = "user_time_exceeded"  # When the user has been using the experiment for too long.

# Names for the configuration variables.
CFG_XILINX_COMPILING_FILES_PATH = "xilinx_compiling_files_path"
CFG_XILINX_COMPILING_TOOLS_PATH = "xilinx_compiling_tools_path"
CFG_XILINX_VHD_ALLOWED = "xilinx_vhd_allowed"
CFG_XILINX_BIT_ALLOWED = "xilinx_bit_allowed"

# A timer will start after synthesization and programming finishes. If this max_use_time is exceeded, then
# the user will soon be kicked out of the experiment. This timeout is internally enforced. It will kick
# the user out, regardless of the time_allowed permission time he has left.
# If zero, no limit will be enforced.
CFG_XILINX_MAX_USE_TIME = "xilinx_max_use_time"

CFG_DEBUG_FLAG = "debug"
CFG_FAKE_FLAG = "fake"
CFG_FAKE_LEDS_FLAG = "fake_leds" # Subset of FAKE_FLAG.

DEBUG = False  # Can be overriden by the config.


# TODO: which exceptions should the user see and which ones should not?
class UdXilinxExperiment(Experiment.Experiment):
    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    @logged("info")
    def do_get_api(self):
        return "2"

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(UdXilinxExperiment, self).__init__(*args, **kwargs)
        self._coord_address = coord_address
        self._locator = locator
        self._cfg_manager = cfg_manager

        # Board & Programming related attributes
        self._board_type = self._cfg_manager.get_value('xilinx_board_type', "")  # Read the board type: IE: FPGA
        self._programmer_type = self._cfg_manager.get_value('xilinx_programmer_type',
                                                            "")  # Read the programmer type: IE: DigilentAdapt
        self._programmer = self._load_programmer(self._programmer_type, self._board_type)
        self._command_sender = self._load_command_sender()

        # Debugging and testing related attributes
        global DEBUG
        DEBUG = self._cfg_manager.get_value(CFG_DEBUG_FLAG, DEBUG)
        self._fake = self._cfg_manager.get_value(CFG_FAKE_FLAG, False)
        self._fake_leds = self._cfg_manager.get_value(CFG_FAKE_LEDS_FLAG, False)

        self.webcam_url = self._load_webcam_url()

        self._programming_thread = None
        self._current_state = STATE_NOT_READY
        self._programmer_time = self._cfg_manager.get_value('xilinx_programmer_time', "25")  # Seconds
        self._synthesizer_time = self._cfg_manager.get_value('xilinx_synthesizer_time', "90")  # Seconds
        self._adaptive_time = self._cfg_manager.get_value('xilinx_adaptive_time', True)
        self._switches_reversed = self._cfg_manager.get_value('switches_reversed', False)  # Seconds
        self._max_use_time = self._cfg_manager.get_value('xilinx_max_use_time', 0)

        # TODO: It doesn't really make sense to have such a default, but it is here so that the deployed
        # servers don't break if they aren't updated ot include this setting.
        self._leds_service_url = self._cfg_manager.get_value('leds_service_url', "http://192.168.0.73/values.json")

        self._compiling_files_path = self._cfg_manager.get_value(CFG_XILINX_COMPILING_FILES_PATH, "")
        self._compiling_tools_path = self._cfg_manager.get_value(CFG_XILINX_COMPILING_TOOLS_PATH, "")
        self._synthesizing_result = ""

        self._vhd_allowed = self._cfg_manager.get_value(CFG_XILINX_VHD_ALLOWED, True)
        self._bit_allowed = self._cfg_manager.get_value(CFG_XILINX_BIT_ALLOWED, True)

        self._ucf_file = None

        self._switches_state = list("0000000000")

        # This is for remembering when the experiment real use starts, so that we can enforce max_use_time
        self._use_time_start = None

        # These are only for led-state reading. This is an experimental
        # feature.
        self._led_reader = None
        self._led_state = None

        # These are for virtual-worlds
        self._virtual_world = ""
        self._virtual_world_state = ""
        self._last_virtualworld_update = time.time()
        self._watertank = None
        self._watertank_time_without_demand_change = 0

    def _load_programmer(self, programmer_type, board_type):
        """
        Loads the Programmer that will handle the actual programming of the logic into the Board.
        :param programmer_type: The type of programmer (for instance, DigilentAdapt, or XilinxImpact)
        :param board_type: The type of Xilinx board (for instance, FPGA or PLD)
        :return:
        """
        return XilinxProgrammer.create(programmer_type, self._cfg_manager, board_type)

    def _load_command_sender(self):
        device_name = self._cfg_manager.get_value('xilinx_device_to_send_commands')
        return UdXilinxCommandSender.create(device_name, self._cfg_manager)

    def _load_webcam_url(self):
        cfg_webcam_url = "%s_webcam_url" % self._board_type.lower()
        return self._cfg_manager.get_value(cfg_webcam_url, "http://localhost")

    def get_state(self):
        return self._current_state

    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    @logged("info", except_for='file_content')
    def do_send_file_to_device(self, file_content, file_info):
        """
        Will spawn a new thread which will program the xilinx board with the
        provided file.
        """

        if DEBUG: print("[DBG]: File Received: Info: {0}".format(file_info))

        # If we are in fake-mode we'll just return a programming state.
        if self._fake:
            return "STATE=" + STATE_PROGRAMMING

        # Reset the tracked state
        self._switches_state = list("0000000000")

        # TODO:
        # We will distinguish the file type according to its size.
        # This is an extremely bad method, which should be changed in the
        # future. Currently we assume that if the file length is small,
        # then it's a VHDL file rather than a BITSTREAM. Explicit UCF
        # is not yet supported.
        extension = file_info
        if extension == "vhd":
            try:
                if self._vhd_allowed == False:
                    self._current_state = STATE_NOT_ALLOWED
                    return "STATE=" + STATE_NOT_ALLOWED
                if DEBUG: print "[DBG]: File received: Info: " + file_info
                self._handle_vhd_file(file_content, file_info)
                return "STATE=" + STATE_SYNTHESIZING
            except Exception as ex:
                if DEBUG: print "EXCEPTION: " + ex
                raise ex
        else:  # We assume, a .bit file.
            if not self._bit_allowed:
                self._current_state = STATE_NOT_ALLOWED
                return "STATE=" + STATE_NOT_ALLOWED
            self._programming_thread = self._program_file_t(file_content)
            return "STATE=" + STATE_PROGRAMMING

    def _handle_ucf_file(self, file_content, file_info):
        print os.getcwd()
        c = Compiler(self._compiling_files_path)
        content = base64.b64decode(file_content)
        c.feed_ucf(content)

    def _handle_vhd_file(self, file_content, file_info):
        if DEBUG: print "[DBG] In _handle_vhd_file. Info is " + file_info
        self._compile_program_file_t(file_content)

    @threaded()
    @logged("info", except_for='file_content')
    def _compile_program_file_t(self, file_content):
        """
        Running in its own thread, this method will compile the provided
        VHDL code and then program the board if the result is successful.
        """
        self._current_state = STATE_SYNTHESIZING
        c = Compiler(self._compiling_files_path, self._compiling_tools_path, self._board_type.lower())
        # c.DEBUG = True
        content = base64.b64decode(file_content)

        done_already = c.is_same_as_last(content)

        if not done_already:
            if self._board_type.lower() == "fpga":
                # TODO: This is quite ugly. We make sure the Compilar class replaces some string to make the
                # UCF / augmented reality works.
                c.feed_vhdl(content, True, False)
            else:
                c.feed_vhdl(content, False, False)
            if DEBUG: print "[DBG]: VHDL fed. Now compiling."
            success = c.compileit()

        else:
            if DEBUG: print "[DBG]: VHDL is already available. Reusing."
            success = c.get_last_result()

            # TODO: Fix this. Wrong work-around around a bug, so that it works during
            # controlled circumstances.
            # if success is None: success = True

        if success is not None and not success:
            self._current_state = STATE_SYNTHESIZING_ERROR
            self._compiling_result = c.errors()
        else:
            # If we are using adaptive timing, modify it according to this last input.
            # TODO: Consider limiting the allowed range of variation, in order to dampen potential anomalies.
            elapsed = c.get_time_elapsed()
            if (self._adaptive_time):
                self._programmer_time = elapsed

            targetfile = c.retrieve_targetfile()
            if DEBUG: print "[DBG]: Target file retrieved after successful compile. Now programming."
            c._compiling_result = "Synthesizing done."
            self._program_file_t(targetfile)

    @threaded()
    @logged("info", except_for='file_content')
    def _program_file_t(self, file_content):
        """
        Running in its own thread, this method will program the board
        while updating the state of the experiment appropriately.
        """
        try:
            start_time = time.time()  # To track the time it takes
            self._current_state = STATE_PROGRAMMING
            self._program_file(file_content)
            self._current_state = STATE_READY
            elapsed = time.time() - start_time  # Calculate the time the programming process took

            # Remember when real usage starts, so that we can enforce use-time specific limits.
            self._use_time_start = time.time()
            if DEBUG:
                print "[DBG]: STATE became STATE_READY. UseTimeStart = %s." % self._use_time_start

            # If we are in adaptive mode, change the programming time appropriately.
            # TODO: Consider limiting the variation range to dampen anomalies.
            if self._adaptive_time:
                self._programmer_time = elapsed
        except Exception as e:
            # Note: Currently, running the fake xilinx will raise this exception when
            # trying to do a CleanInputs, for which apparently serial is needed.
            self._current_state = STATE_FAILED
            log.log(UdXilinxExperiment, log.level.Warning, "Error programming file: " + str(e))
            log.log_exc(UdXilinxExperiment, log.level.Warning)

    def _program_file(self, file_content):
        try:
            fd, file_name = tempfile.mkstemp(prefix='ud_xilinx_experiment_program',
                                             suffix='.' + self._programmer.get_suffix())  # Originally the Programmer wasn't the one to contain the suffix info.

            if DEBUG:
                print "[DBG]: 2"
                df2 = open("/tmp/orig_content", "w")
                df2.write("---begin---\n")
                df2.write(file_content)
                df2.close()

                # For debugging purposes write the file to tmp
                df = open("/tmp/toprogram_dbg", "w")
            try:
                try:
                    # TODO: encode? utf8?
                    if isinstance(file_content, unicode):
                        if DEBUG: print "[DBG]: Encoding file content in utf8"
                        file_content_encoded = file_content.encode('utf8')
                    else:
                        if DEBUG: print "[DBG]: Not encoding file content"
                        file_content_encoded = file_content
                    file_content_recovered = ExperimentUtil.deserialize(file_content_encoded)
                    os.write(fd, file_content_recovered)
                    if DEBUG:
                        df.write(file_content_recovered)
                finally:
                    os.close(fd)
                self._programmer.program(file_name)
            finally:
                os.remove(file_name)
                # print file_name
                # import sys
                # sys.stdout.flush()
        except Exception as e:

            if DEBUG:
                tb = traceback.format_exc()
                print "FULL EXCEPTION IS: {0}".format(tb)

            # TODO: test me
            log.log(UdXilinxExperiment, log.level.Info,
                    "Exception joining sending program to device: %s" % e.args[0])
            log.log_exc(UdXilinxExperiment, log.level.Debug)
            raise ExperimentErrors.SendingFileFailureError("Error sending file to device: %s" % e)
        self._clear()

    def _clear(self):
        try:
            self._command_sender.send_command("CleanInputs")
        except Exception as e:
            raise ExperimentErrors.SendingCommandFailureError(
                "Error sending command to device: %s" % e
            )

    @Override(Experiment.Experiment)
    @logged("info")
    def do_dispose(self):
        """
        We make sure that the board programming thread has finished, just
        in case the experiment finished early and its still on it.
        """
        self._use_time_start = None  # Ensure that the time gets reset.

        if self._programming_thread is not None:
            self._programming_thread.join()
            # Cleaning references
            self._programming_thread = None

        if self._watertank is not None:
            # In case it is running.
            self._watertank.autoupdater_stop()

        return "ok"

    @Override(Experiment.Experiment)
    @logged("info")
    def do_start_experiment(self, *args, **kwargs):
        self._current_state = STATE_NOT_READY
        return json.dumps({
            "initial_configuration": """{ "webcam" : "%s", "expected_programming_time" : %s, "expected_synthesizing_time" : %s, "max_use_time" : %s }""" % (
                self.webcam_url, self._programmer_time, self._synthesizer_time, self._max_use_time), "batch": False})

    def virtualworld_update(self, delta):
        """
        Handles virtual world updating. For instance, in the case of the watertank,
        it will control the virtual sensors (switches) depending on the watertank level.
        """
        if self._watertank != None:
            waterLevel = self._watertank.get_water_level()
            self.change_switch(0, waterLevel >= 0.20)
            self.change_switch(1, waterLevel >= 0.50)
            self.change_switch(2, waterLevel >= 0.80)

            # These only apply for the temperature mode, but they are always valid nonetheless.
            temps = self._watertank.get_temperatures()
            self.change_switch(3, temps[0] > 200)  # The 150 is essentially arbitrary
            self.change_switch(4, temps[1] > 200)  # The 150 is essentially arbitrary

        self._watertank_time_without_demand_change += delta

        if self._watertank_time_without_demand_change > 5:
            self._watertank_time_without_demand_change = 0
            self._watertank.set_outputs([random.randint(0, 20)])

    # TODO: Eventually, there should be some way to limit the number of switches that a 
    # user can explicitly control depending on the VirtualWorld simulation and state.
    # For instance, if the first switch represents a water level sensor, it makes no 
    # sense for the user to be able to define its state. For now, it is left as-is
    # mainly for debugging convenience.

    def change_switch(self, switch, on):
        """
        Changes the state of a switch. This can be used, for instance, for
        simulating sensors.
        
        @param switch Number of the switch to change.
        @param on True if we wish to turn it on, false to turn it off.
        """
        if on:
            if self._switches_state[9 - switch] == "0":
                self._command_sender.send_command("ChangeSwitch %s %d" % ("on", 9 - switch))
        else:
            if self._switches_state[9 - switch] == "1":
                self._command_sender.send_command("ChangeSwitch %s %d" % ("off", 9 - switch))

        if on:
            self._switches_state[9 - switch] = "1"
        else:
            self._switches_state[9 - switch] = "0"

        return

    @Override(Experiment.Experiment)
    def do_should_finish(self):
        if DEBUG:
            print "[DBG]: We're on should_finish."
            # Check here that we still have use time left. When the refactor takes place,
        # this should maybe be moved somewhere else.
        if self._max_use_time != 0 and self._use_time_start is not None:
            elapsed = time.time() - self._use_time_start
            if elapsed >= self._max_use_time:
                # We are overtime. We should make the user finish.
                self._current_state = STATE_USE_TIME_EXCEEDED
                print "[DBG]: Time was indeed exceeded. Quitting now."
                # TODO: Maybe we should give some extra seconds so that the state
                # STATE_USE_TIME_EXCEEDED can be received normally.
                return -1

        return 10  # We still haven't exceeded our time. Check again in ten seconds.

    @logged("info")
    @Override(Experiment.Experiment)
    @caller_check(ServerType.Laboratory)
    def do_send_command_to_device(self, command):
        try:
            # Reply with the current state of the experiment. Particularly, the clients
            # will need to know whether the programming has been done and whether we are
            # hence ready to start receiving real commands.
            if command == 'STATE':
                if self._fake:
                    self._current_state = STATE_READY
                if DEBUG:
                    print "[DBG]: STATE CHECK: " + self._current_state
                reply = "STATE=" + self._current_state
                return reply

            elif command.startswith('ChangeSwitch'):
                # Intercept the ChangeSwitch command to track the state of the Switches.
                # This command will in fact be later relied to the Device.
                cs = command.split(" ")
                switch_number = cs[2]

                # TODO: Make sure that switches are being properly used,
                # and that reversion issues are taken into account.
                if cs[1] == "on":
                    self._switches_state[int(switch_number)] = "1"
                else:
                    self._switches_state[int(switch_number)] = "0"

            elif command == 'REPORT_USE_TIME_LEFT':
                if self._max_use_time == 0:
                    time_left = "unlimited"
                elif self._use_time_start is None:
                    time_left = "unknown"
                else:
                    elapsed = time.time() - self._use_time_start
                    remaining = self._max_use_time - elapsed
                    if remaining < 0: remaining = 0
                    time_left = str(remaining)

                if DEBUG:
                    print "[DBG]: REPORT_USE_TIME_LEFT: Time Left: %s" % time_left
                return time_left

            elif command == 'REPORT_SWITCHES':
                # TODO: Currently this returns a list. It is somewhat weird for this to return a list.
                # This should be fixed, after making sure it will not break anything.
                return self._switches_state

            elif command.startswith('VIRTUALWORLD_MODE'):
                vw = command.split(" ")[1]
                self._virtual_world = vw

                # Stop the watertank if it is running.
                if self._watertank is not None:
                    self._watertank.autoupdater_stop()

                if vw == "watertank":
                    self._watertank = watertank_simulation.Watertank(1000, [10, 10], [10], 0.5)
                    self._last_virtualworld_update = time.time()
                    self._watertank.autoupdater_start(1)
                    return "ok"
                elif vw == "watertank_temperatures":
                    self._virtual_world = "watertank"  # So that other parts of the code aren't confused. Not very tidy. TODO: Fixme.
                    self._watertank = watertank_simulation.Watertank(1000, [10, 10], [10], 0.5, True)
                    self._last_virtualworld_update = time.time()
                    self._watertank.autoupdater_start(1)
                    return "ok"
                else:
                    return "unknown_virtualworld"

            elif command.startswith('VIRTUALWORLD_STATE'):

                if (self._watertank != None):
                    self._virtual_world_state = self._watertank.get_json_state([20, 20], [20])

                    now = time.time()
                    # TODO: This should not be done here. For now however, it's the easiest place to put it in.
                    self.virtualworld_update(now - self._last_virtualworld_update)
                    self._last_virtualworld_update = now

                    return self._virtual_world_state

                return "{}";

            elif command == 'HELP':
                return "VIRTUALWORLD_MODE | VIRTUALWORLD_STATE | SYNTHESIZING_RESULT | READ_LEDS | REPORT_SWITCHES | REPORT_USE_TIME_LEFT | STATE | ChangeSwitch"

            elif command == 'SYNTHESIZING_RESULT':
                if (DEBUG):
                    print "[DBG]: SYNTHESIZING_RESULT: " + self._compiling_result
                return self._compiling_result

            elif command == 'READ_LEDS':
                try:
                    self._led_state = self.query_leds_from_json()
                    if DEBUG:
                        print("[DBG]: LED state queried. It is: {0}".format(self._led_state))

                    if self._virtual_world == "watertank":
                        # Note: The following needs a somewhat major redesign.
                        self._update_watertank(self._led_state)

                    return "".join(self._led_state)
                except Exception as e:
                    traceback.print_exc()
                    return "ERROR: " + traceback.format_exc()

            # Otherwise we assume that the command is intended for the actual device handler
            # If it isn't, it throw an exception itself.

            if self._switches_reversed:
                if command.startswith("ChangeSwitch"):
                    command = command.replace(command[-1], str(9 - int(command[-1])))
            self._command_sender.send_command(command)
        except Exception as e:
            if DEBUG:
                traceback.print_exc(e)
            raise ExperimentErrors.SendingCommandFailureError(
                "Error sending command to device: %s" % e
            )

    def query_leds_from_json(self):
        """
        The server reports the LEDs from left to right (leftmost LED being 0, topmost being 9)
        :return:
        """

        if self._fake or self._fake_leds:
            return ['0']*10

        jsonurl = self._leds_service_url
        o = urllib2.urlopen(jsonurl)
        jsonstr = o.read()
        js = json.loads(jsonstr)
        inputsMap = {}
        inputs = js["inputs"]
        inputsList = []
        for input in inputs:
            number = input["inputNumber"]
            value = input["value"]
            inputsMap[int(number)] = value

        # We store only the first 8. (why?).
        for i in range(8):
            inputsList.append(inputsMap[i])

        return inputsList

    def _update_watertank(self, led_state):
        """
        This function should probably be moved somewhere, and made generic. Ideally, we would want
        watertank to be some kind of plugin.
        """
        first_pump = led_state[7] == '1'
        second_pump = led_state[6] == '1'
        if first_pump:
            first_pump = 10
        else:
            first_pump = 0
        if second_pump:
            second_pump = 10
        else:
            second_pump = 0
        self._watertank.set_input(0, first_pump)
        self._watertank.set_input(1, second_pump)


if __name__ == "__main__":
    from voodoo.configuration import ConfigurationManager
    from voodoo.sessions.session_id import SessionId

    cfg_manager = ConfigurationManager()
    try:
        cfg_manager.append_path("../../../launch/sample/main_machine/main_instance/experiment_fpga/server_config.py")
    except:
        cfg_manager.append_path("../launch/sample/main_machine/main_instance/experiment_fpga/server_config.py")

    experiment = UdXilinxExperiment(None, None, cfg_manager)

    lab_session_id = SessionId('my-session-id')
    experiment.do_start_experiment()

    experiment._max_use_time = 10
    print experiment.do_send_command_to_device("REPORT_USE_TIME_LEFT")
    print experiment.do_send_command_to_device("STATE")
    print experiment.do_send_command_to_device("STATE")
    print experiment.do_should_finish()
    print experiment.do_send_command_to_device("STATE")
    print experiment.do_should_finish()

    print experiment.do_send_command_to_device("VIRTUALWORLD_STATE")
    print experiment.do_send_command_to_device("REPORT_SWITCHES")
    print experiment.do_send_command_to_device("ChangeSwitch on 1")
    print experiment.do_send_command_to_device("REPORT_SWITCHES")
    print experiment.do_send_command_to_device("VIRTUALWORLD_MODE watertank")
    print experiment.do_send_command_to_device("VIRTUALWORLD_STATE")
    time.sleep(1)
    print experiment.do_send_command_to_device("VIRTUALWORLD_STATE")
    print experiment.do_send_command_to_device("REPORT_SWITCHES")
    time.sleep(1)
    print experiment.do_send_command_to_device("VIRTUALWORLD_STATE")
    experiment._watertank.current_volume = 0
    time.sleep(5)
    print experiment.do_send_command_to_device("REPORT_SWITCHES")
    time.sleep(1)
    while (True):
        print experiment.do_send_command_to_device("VIRTUALWORLD_STATE")
        experiment._watertank.current_volume = 0
        print experiment.do_send_command_to_device("READ_LEDS")
        print experiment.do_send_command_to_device("REPORT_SWITCHES")
        time.sleep(1)
        print experiment.do_send_command_to_device("REPORT_SWITCHES")
        print experiment.do_send_command_to_device("VIRTUALWORLD_STATE")
