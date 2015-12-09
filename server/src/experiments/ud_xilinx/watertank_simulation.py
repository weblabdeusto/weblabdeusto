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
    """
    Watertank Model

    Output example:
    {"water": 0.0, "inputs": [0.5, 0.5], "temperatures": [716, 20], "outputs": [1.0]}

    Changes that have been applied lately to this model (Dec 2015)
      - There is no longer a separate temperatures mode. Now there is a single model with temperatures.
      - There are no longer temperature working ranges, temperature warnings, or temperature overloads. The
        model will not prevent the pumps from working. Instead, the temperature will increase indefinitely. The experiment
        client can thus deal with temperatures however it wishes (and it can in fact ignore them), with no effect.
      - As a result of the previous change, temperature is no longer reported as in the [0,1] range according to the range.
        Now it is reported in raw form.
    """

    def __init__(self, tank_capacity, inputs, outputs, water_level):
        self.initialize(tank_capacity, inputs, outputs, water_level)

    def initialize(self, tank_capacity, inputs, outputs, water_level):
        """
        Initializes the simulation with the specified data.
        @param tank_capacity Capacity of the water tank, in liters.
        @param Array containing the flow volume of the inputs (such as water pumps), in liters per second. 
        The flow can be modified dynamically, but no inputs can be added. 
        @param Array containing the outputs (such as a water hose or evaporation), in liters per second. 
        The flow can be modified dynamically, but no inputs can be added.
        @param water_level The starting water level. Value from 0 to 1.
        """
        self.tank_capacity = tank_capacity
        self.inputs = inputs
        self.outputs = outputs
        self.current_volume = water_level * tank_capacity

        self.firstPumpTemperature = 20
        self.secondPumpTemperature = 20
        self.firstPumpWorkRange = [20, 200]
        self.secondPumpWorkRange = [20, 200]
        self.pumpTemperatureVariationPerSeconds = 6  # Enough for 30 seconds?

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

        # Handle inputs
        pump1, pump2 = self.inputs

        # If the first pump is turned on we increase the temperature and the total water input
        if pump1 > 0:
            # We multiply by 1.1 so that its temperature raises faster.
            self.firstPumpTemperature += delta * self.pumpTemperatureVariationPerSeconds * 1.1
            total_input += pump1 * delta
        else:
            self.firstPumpTemperature -= delta * self.pumpTemperatureVariationPerSeconds
            self.firstPumpTemperature = max(20, self.firstPumpTemperature)
            total_input -= pump1 * delta

        # If the second pump is turned on we increase the temperature and the total water input
        if pump2 > 0:
            self.secondPumpTemperature += delta * self.pumpTemperatureVariationPerSeconds
            total_input += pump2 * delta
        else:
            self.secondPumpTemperature -= delta * self.pumpTemperatureVariationPerSeconds
            self.secondPumpTemperature = max(20, self.secondPumpTemperature)
            total_input -= pump2 * delta

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

    def get_temperatures(self):
        """
        Get temperatures.
        :return:
        """
        return [self.firstPumpTemperature, self.secondPumpTemperature]

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

        state = {"water": self.get_water_level(), "inputs": inputs, "outputs": outputs}

        # Report the RAW temperature
        temperatures = [0, 0]
        temperatures[0] = self.firstPumpTemperature
        temperatures[1] = self.secondPumpTemperature
        state["temperatures"] = temperatures

        return json.dumps(state)


if __name__ == '__main__':

    from mock import patch
    import unittest

    def fake_sleep(t):
        # TODO
        a = [1 for i in range(100000)]  # very fast kludge to add minor delay
        b = len(a)
        pass

    class TestWatertankSimulation(unittest.TestCase):

        def test_nothing(self):
            pass

        def _get_state(self, w):
            js = w.get_json_state([20, 20], [100])
            d = json.loads(js)
            return d

        @patch("time.sleep", fake_sleep)
        def test_waterlevel_increase_decrease(self):
            w = Watertank(1000, [100, 100], [100], 0.5)
            w.autoupdater_start(1)

            initial_level = self._get_state(w)["water"]

            i = 0
            while (i < 15):
                time.sleep(0.5)
                i += 1

            other_level = self._get_state(w)["water"]

            # Check that the water level did increase
            self.assertGreater(other_level, initial_level)

            w.set_outputs([400])

            i = 0
            while (i < 15):
                time.sleep(0.5)
                i += 1

            dec_level = self._get_state(w)["water"]

            # Check that the water level did decrease
            self.assertGreater(other_level, dec_level)

        @patch("time.sleep", fake_sleep)
        def test_temperature_increase_decrease(self):
            w = Watertank(1000, [100, 100], [100], 0.5)
            w.autoupdater_start(1)

            t0 = self._get_state(w)["temperatures"][0]

            i = 0
            while (i < 15):
                time.sleep(0.5)
                i += 1

            t1 = self._get_state(w)["temperatures"][0]

            # Check that the water level did increase
            self.assertGreater(t1, t0)

            w.set_inputs([0, 0])

            i = 0
            while (i < 15):
                time.sleep(0.5)
                i += 1

            t2 = self._get_state(w)["temperatures"][0]

            # Check that the water level did decrease
            self.assertGreater(t1, t2)

        # @patch("time.sleep", fake_sleep)
        # def test_first(self):
        #     w = Watertank(1000, [100, 100], [100], 0.5)
        #     w.autoupdater_start(1)
        #
        #     i = 0
        #     while (i < 15):
        #         print w.tank_capacity, w.get_water_level(), w.get_water_volume(), w.get_json_state([20, 20], [100])
        #         time.sleep(0.5)
        #         i += 1
        #
        #     print "...."
        #     i = 0
        #     w.set_outputs([100])
        #     w.set_inputs([10, 10])
        #     while (i < 30):
        #         print w.tank_capacity, w.get_water_level(), w.get_water_volume(), w.get_json_state([20, 20], [100])
        #         time.sleep(0.5)
        #         i += 1
        #
        #     w.autoupdater_join()
        #
        # @patch("time.sleep", fake_sleep)
        # def test_second(self):
        #     w = Watertank(1000, [100, 100], [100], 0.5)
        #
        #     i = 0
        #     while i < 15:
        #         print w.tank_capacity, w.get_water_level(), w.get_water_volume(), w.get_json_state([20, 20], [100])
        #         w.update(1)
        #         i += 1
        #
        #     print "...."
        #     i = 0
        #     w.set_outputs([100])
        #     w.set_inputs([10, 10])
        #     while i < 15:
        #         print w.tank_capacity, w.get_water_level(), w.get_water_volume(), w.get_json_state([20, 20], [100])
        #         w.update(1)
        #         i += 1


    unittest.main()