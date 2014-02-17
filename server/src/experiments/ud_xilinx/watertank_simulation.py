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
# Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
#


import threading
import time
import json


class Watertank(object):
    def __init__(self, tank_capacity, inputs, outputs, water_level, temperatures_mode=False):
        self.initialize(tank_capacity, inputs, outputs, water_level, temperatures_mode)


    def initialize(self, tank_capacity, inputs, outputs, water_level, temperatures_mode=False):
        """
        Initializes the simulation with the specified data.
        @param tank_capacity Capacity of the water tank, in liters.
        @param Array containing the flow volume of the inputs (such as water pumps), in liters per second. 
        The flow can be modified dynamically, but no inputs can be added. 
        @param Array containing the outputs (such as a water hose or evaporation), in liters per second. 
        The flow can be modified dynamically, but no inputs can be added.
        @param water_level The starting water level. Value from 0 to 1.
        @param temperatures_mode If the temperatures_mode is enabled the Watertank will also feature pump temperatures.
        """
        self.tank_capacity = tank_capacity
        self.inputs = inputs
        self.outputs = outputs
        self.current_volume = water_level * tank_capacity

        self.temperatures_mode = temperatures_mode

        self.firstPumpTemperature = 20
        self.secondPumpTemperature = 20
        self.firstPumpWorkRange = [20, 200]
        self.secondPumpWorkRange = [20, 200]
        self.firstPumpOverheated = False  # If we reached the maximum temperature
        self.secondPumpOverheated = False
        self.pumpWarningPercent = 0.80  # This marks the point where the warning is set. A pump cannot be started with the warning on.
        self.pumpTemperatureVariationPerSeconds = 12  # Enough for 15 seconds straight use.

        self.simlock = threading.RLock()
        self._thread = None
        self._autoupdating = False
        self._autoupdating_interval = 1000

    def update(self, delta):
        """
        Updates the simulation. Can be done automatically if the autoupdater is used.
        @param delta Delta in seconds.
        @see autoupdater_start
        """
        total_output = 0
        for out in self.outputs:
            total_output += out * delta

        # Calculates how much the pumps are putting in.
        total_input = 0

        # Handle inputs in the advanced, temperatures_mode.
        if self.temperatures_mode:
            pump1, pump2 = self.inputs
            if pump1 > 0:
                # Check overheat
                if self.firstPumpTemperature > self.firstPumpWorkRange[1]:
                    self.firstPumpOverheated = True
                    self.firstPumpTemperature -= delta * self.pumpTemperatureVariationPerSeconds
                elif not self.firstPumpOverheated:
                    self.firstPumpTemperature += delta * self.pumpTemperatureVariationPerSeconds
                    total_input += pump1 * delta
            elif self.firstPumpTemperature > self.firstPumpWorkRange[0]:
                self.firstPumpTemperature -= delta * self.pumpTemperatureVariationPerSeconds

            if pump2 > 0:
                # Check overheat
                if self.secondPumpTemperature > self.secondPumpWorkRange[1]:
                    self.secondPumpOverheated = True
                    self.secondPumpTemperature -= delta * self.pumpTemperatureVariationPerSeconds
                elif not self.secondPumpOverheated:
                    self.secondPumpTemperature += delta * self.pumpTemperatureVariationPerSeconds
                    total_input += pump2 * delta
            elif self.secondPumpTemperature > self.secondPumpWorkRange[0]:
                self.secondPumpTemperature -= delta * self.pumpTemperatureVariationPerSeconds

            # Clear the overheated state if we have to.
            if self.firstPumpOverheated and self.firstPumpTemperature <= self.firstPumpWorkRange[0] + self.pumpWarningPercent * (self.firstPumpWorkRange[1] - self.firstPumpWorkRange[0]):
                self.firstPumpOverheated = False

            if self.secondPumpOverheated and self.secondPumpTemperature <= self.secondPumpWorkRange[0] + self.pumpWarningPercent * (self.secondPumpWorkRange[1] - self.secondPumpWorkRange[0]):
                self.secondPumpOverheated = False

        # Handle inputs in the standard mode.
        else:
            for ins in self.inputs:
                total_input += ins * delta

        increment = total_input - total_output

        with self.simlock:
            self.current_volume += increment

            # Ensure the volume stays realistic
            if self.current_volume >= self.tank_capacity:
                self.current_volume = self.tank_capacity
            elif self.current_volume < 0:
                self.current_volume = 0.0

    def t_updater(self):
        """
        This internal method is used by the autoupdating thread to update
        the simulation every few seconds (specified as the autoupdater interval).
        """
        while self._autoupdating:
            time.sleep(self._autoupdating_interval)
            self.update(self._autoupdating_interval)

    def autoupdater_start(self, interval):
        """
        Starts the autoupdating thread. That is, a thread that will call update
        every so often. If started, it should eventually be stopped. Otherwise,
        it will run forever in the background.
        @param interval Interval between updates, in seconds.
        @see autoupdater_stop
        """
        self._autoupdating = True
        self._autoupdating_interval = interval
        self._thread = threading.Thread(None, self.t_updater)
        self._thread.start()

    def autoupdater_stop(self):
        """
        Stops the autoupdating thread. This method is non-blocking. It will signal
        the thread to stop, but may take a while before it *really* does stop.
        There is a blocking version of this method.
        @see autoupdater_join
        """
        self._autoupdating = False

    def autoupdater_join(self):
        """
        Stops the autoupdating thread, and joins that thread until it really does stop.
        May block forever if for some reason the thread won't stop, but that
        should not happen.
        """
        self._autoupdating = False
        self._thread.join(0)

    def set_input(self, input_number, input_flow):
        """
        Sets the value for an input in the simulation. 
        @param input_number Number identifying the input. The input should exist.
        @param input_flow New flow of the input, in liters per second.
        """
        with self.simlock:
            self.inputs[input_number] = input_flow

    def set_output(self, output_number, output_flow):
        """
        Sets the value for an output in the simulation.
        @param output_number Number identifying the output. The output should exist.
        @param output_flow New flow of the output, in liters per second.
        """
        with self.simlock:
            self.outputs[output_number] = output_flow

    def set_inputs(self, inputs):
        """
        Redefines the whole array of inputs.
        @param inputs Array containing the flow of every input.
        """
        with self.simlock:
            self.inputs = inputs

    def set_outputs(self, outputs):
        """
        Redefines the whole array of outputs.
        @param outputs Array containing the flow of every output.
        """
        with self.simlock:
            self.outputs = outputs

    def get_water_volume(self):
        """
        Gets the current water volume in liters. It will vary dynamically according to the 
        simulation's state.
        """
        with self.simlock:
            return self.current_volume

    def get_water_level(self):
        """
        Gets the current water level, as a number from 0 to 1 (empty to full). It will vary dynamically
        according to the simulation's state.
        """
        with self.simlock:
            return 1.0 * self.current_volume / self.tank_capacity

    def get_temperature_warnings(self):
        """
        Gets the state of the temperature warnings.

        @return: Returns the state of the temperature warning sensors as an array of 2 elements, each element being 1 or 0.
        """
        temp_warnings = [0, 0]
        if self.firstPumpTemperature > (self.firstPumpWorkRange[1] - self.firstPumpWorkRange[0]) * self.pumpWarningPercent + self.firstPumpWorkRange[0]:
            temp_warnings[0] = 1
        else:
            temp_warnings[0] = 0

        if self.secondPumpTemperature > (self.secondPumpWorkRange[1] - self.secondPumpWorkRange[0]) * self.pumpWarningPercent + self.firstPumpWorkRange[0]:
            temp_warnings[1] = 1
        else:
            temp_warnings[1] = 0
        return temp_warnings

    def get_json_state(self, input_capacities, output_capacities):
        """
        Gets a json-encoded description of the simulation's state. 
        As of now, it takes output and input capacities as arguments because the JSON state
        is described through relative values. (For instance, first output at 0.3 capacity).
        
        @param input_capacities An array containing the maximum capacities of the input.
        @param output_capacities An array containing the maximum capacities of the output.
        """
        if len(self.inputs) != len(input_capacities):
            return "{}"

        inputs = []
        for inp, cap in zip(self.inputs, input_capacities):
            inputs.append(1.0 * inp / cap)

        outputs = []
        for inp, cap in zip(self.outputs, output_capacities):
            outputs.append(1.0 * inp / cap)

        # If we are in the advanced temperatures mode we have to set the inputs of a pump to zero if
        # a bomb is currently overheating.
        if self.temperatures_mode:
            if self.firstPumpOverheated:
                inputs[0] = 0
            if self.secondPumpOverheated:
                inputs[1] = 0

        state = {"water": self.get_water_level(), "inputs": inputs, "outputs": outputs}

        # Whether the temp warnings are set or not.
        if self.temperatures_mode:
            temp_warnings = self.get_temperature_warnings()

            state["temp_warnings"] = temp_warnings

            temperatures = [0, 0]
            temperatures[0] = (self.firstPumpTemperature - self.firstPumpWorkRange[0]) * 1.0 / (self.firstPumpWorkRange[1] - self.firstPumpWorkRange[0])
            temperatures[1] = (self.secondPumpTemperature - self.secondPumpWorkRange[0]) * 1.0 / (self.secondPumpWorkRange[1] - self.secondPumpWorkRange[0])
            state["temperatures"] = temperatures

        return json.dumps(state)


if __name__ == '__main__':

    from mock import patch

    def fake_sleep(time):
        pass

    @patch("time.sleep", fake_sleep)
    def test():

        w = Watertank(1000, [100, 100], [100], 0.5, True)
        w.autoupdater_start(1)

        i = 0
        while (i < 15):
            print w.tank_capacity, w.get_water_level(), w.get_water_volume(), w.get_json_state([20, 20], [100])
            time.sleep(0.5)
            i += 1

        print "...."
        i = 0
        w.set_outputs([100])
        w.set_inputs([10, 10])
        while (i < 30):
            print w.tank_capacity, w.get_water_level(), w.get_water_volume(), w.get_json_state([20, 20], [100])
            time.sleep(0.5)
            i += 1

        w.autoupdater_join()


    def test2():

        w = Watertank(1000, [100, 100], [100], 0.5, True)

        i = 0
        while i < 15:
            print w.tank_capacity, w.get_water_level(), w.get_water_volume(), w.get_json_state([20, 20], [100])
            w.update(1)
            i += 1

        print "...."
        i = 0
        w.set_outputs([100])
        w.set_inputs([10, 10])
        while i < 15:
            print w.tank_capacity, w.get_water_level(), w.get_water_volume(), w.get_json_state([20, 20], [100])
            w.update(1)
            i += 1


    print "FIRST TEST: "
    test()
    print "SECOND TEST: "
    test2()