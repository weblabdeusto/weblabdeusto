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
# 

import time
import random
import operator
from socket import AF_INET, SOCK_STREAM, socket

from voodoo.threaded import threaded
import weblab.experiment.Experiment as Experiment
from voodoo.override import Override

import simplejson

class Switch(object):
    def __init__(self, turned = False):
        self.turned = turned

    def set_turned(self, turned):
        self.turned = turned

    def __repr__(self):
        return "<Switch turned='%s'/>" % self.turned

    def to_dict(self):
        return self.turned

class Gate(object):
    operations = {
        'and'  : operator.and_,
        'or'   : operator.or_,
        'xor'  : operator.xor,
        'nand' : lambda x, y: not (x and y),
        'nor'  : lambda x, y: not (x or y),
    }

    @staticmethod
    def get_random_operator():
        return random.choice(Gate.operations.keys())

    def __init__(self, operator, left, right):
        self.left     = left
        self.right    = right
        self.set_operator(operator) 

    def __repr__(self):
        return ("<Gate>\n" + 
                    str(self.left) + "\n" +
                    "<operator name='%s'/>\n" % self.operator +
                    str(self.right) + "\n" +
                    "</Gate>")

    def set_left(self, gate):
        self.left  = gate

    def set_right(self, gate):
        self.right = gate

    def set_operator(self, operator):
        if not operator in self.operations:
            raise Exception("Invalid operation: " + operator)
        self.operator = operator

    @property
    def turned(self):
        return self.operations[self.operator](self.left.turned, self.right.turned)

    def to_dict(self):
        return {
                'left'  : self.left.to_dict(),
                'op'    : self.operator,
                'right' : self.right.to_dict()
            }

class Circuit(object):
    def __init__(self, root, unknown):
        self.root     = root
        self.unknown  = unknown

    def set_unknown(self, operator):
        self.unknown.set_operator(operator)

    @property
    def turned(self):
        return self.root.turned

    def is_correct_sample(self):
        anyTrue  = False
        anyFalse = False
        for operation in Gate.operations:
            self.set_unknown(operation)
            if self.turned:
                anyTrue  = True
            else:
                anyFalse = True
        return anyTrue and anyFalse

    def to_dict(self):
        return self.root.to_dict()

class CircuitGenerator(object):
    def _generate_random(self):
        # Switches: 4 switches
        switchs = [ Switch(random.choice((True, False)) ) for _ in range(4)]

        inputs  = switchs
        rows    = []
        for x in range(3, 0, -1):
            current_row   = []
            for i in range(x):
                operator = Gate.get_random_operator()
                gate = Gate(operator, inputs[i], inputs[i + 1])
                current_row.append(gate)
            inputs = current_row
            rows.append(current_row)
        unknown = rows[0][1]
        return Circuit(gate, unknown)

    def generate(self):
        while True:
            circuit = self._generate_random()
            if circuit.is_correct_sample():
                return circuit

class LogicExperiment(Experiment.Experiment):
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(LogicExperiment,self).__init__(*args, **kwargs)
        self.circuit_generator = CircuitGenerator()
        self.encoder           = simplejson.JSONEncoder()

    @Override(Experiment.Experiment)
    def do_dispose(self):
        try:
            socket(AF_INET, SOCK_STREAM)
            self.send(";0")
        except:
            pass
        return ""

    @Override(Experiment.Experiment)
    def do_start_experiment(self):
        self.tries = 0
        self.current_circuit = self.circuit_generator.generate()

        try:
            self.send("Welcome!;0")
        except Exception, e:
            print "excepcion cuando tocaba LCD Welcome!", str(e)
        return ""

    @threaded()
    def turn_off(self):
        time.sleep(7)
        self.send(";0")

    @threaded()
    def send(self, message):
        TEMPLATE = "POST / HTTP/1.1\r\nConnection: close\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: %(SIZE)s\r\n\r\n%(MSG)s"
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.connect(('192.168.0.50', 80))
            msg = "lcd=%s" % message
            length = len(msg)
            s.send(TEMPLATE % {'SIZE' : length, 'MSG' : msg})
            s.close()
        except Exception, e:
            import traceback
            traceback.print_exc()
            pass

    @Override(Experiment.Experiment)
    def do_send_command_to_device(self, command):
        if command.startswith('SOLVE '):
            try: # "SOLVE XOR"
                operation = command[len('SOLVE '):].strip().lower()
                self.current_circuit.set_unknown(operation)
            except:
                return "Error: invalid operation: %s" % command
            else:
                if self.current_circuit.turned:
                    self.tries += 1
                    self.current_circuit = self.circuit_generator.generate()
                    self.send("OK! %s;1" % self.tries)
                    self.turn_off()
                    return "OK: %s" % self.tries
                else:
                    self.tries = 0
                    self.send("Fail :-(;0")
                    return "FAIL"
        elif command == 'GET_CIRCUIT':
            return self.encoder.encode(self.current_circuit.to_dict())
        else:
            return 'Error: Invalid command: %s' % command

    @Override(Experiment.Experiment)
    def do_send_file_to_device(self, content, file_info):
        return "ok"

