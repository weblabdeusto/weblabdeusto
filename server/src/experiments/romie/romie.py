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
# Author: Iban Eguia <iban.eguia@opendeusto.es>
#

import weblab.experiment.experiment as Experiment

from voodoo.override import Override
from voodoo.log import logged

import urllib2
import json
import random
import sqlite3
import time
import copy

class RoMIExperiment(Experiment.Experiment):

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(RoMIExperiment, self).__init__(*args, **kwargs)
        self._cfg_manager = cfg_manager
        self.read_base_config()

    def read_base_config(self):
        """
        Reads the base config parameters from the config file.
        """

        self.database = self._cfg_manager.get_value('romie_sqlite')

    @Override(Experiment.Experiment)
    @logged("info")
    def do_get_api(self):
        return "2"

    @Override(Experiment.Experiment)
    @logged("info")
    def do_start_experiment(self, client_initial_data, server_initial_data):
        """
        Callback run when the experiment is started.
        """
        if(self._cfg_manager.get_value('debug')):
            print "[RoMIE] do_start_experiment called"

        data = json.loads(server_initial_data)
        self.username = data['request.username']
        self.server = self._cfg_manager.get_value('romie_server')
        self.questions = copy.deepcopy(self._cfg_manager.get_value('questions'))
        self.question = {}
        self.q_difficulty = 0
        self.points = 0
        self.last_tag = ''
        self.finish_time = 0
        self.last_correct = 0

        return ""

    @Override(Experiment.Experiment)
    @logged("info")
    def do_send_command_to_device(self, command):
        """
        Callback run when the client sends a command to the experiment
        @param command Command sent by the client, as a string.
        """
        if(self._cfg_manager.get_value('debug')):
            print "[RoMIE] Command received: %s" % command

        if command == 'F':
            tag = urllib2.urlopen(self.server+'f', timeout = 60).read()
            if tag.startswith('Tag') and tag != self.last_tag:

                self.last_tag = tag

                self.q_difficulty = int(self.points/65000)
                if self.q_difficulty > 10:
                    self.q_difficulty = 10

                index = random.randint(0, len(self.questions[self.q_difficulty])-1)
                self.question = self.questions[self.q_difficulty][index]

                response_question = {
                    'question': self.question['question'],
                    'answers': self.question['answers']
                }

                return json.dumps(response_question)
            else:
                return 'OK'
        elif command == 'L':
            return urllib2.urlopen(self.server+'l', timeout = 60).read()
        elif command == 'R':
            return urllib2.urlopen(self.server+'r', timeout = 60).read()
        elif command.startswith('ANSWER'):

            response = int(command.split()[1])
            correct = self.question['correct'] == response

            if correct:
                time_bonus = 30-(time.time()-self.last_correct)
                bonus = (self.q_difficulty/10+1)*(time_bonus/5 if time_bonus > 5 else 1)
                self.last_correct = time.time()
                self.points += self.question['points']*bonus
                self.finish_time += self.question['time']*bonus
                self.update_points()
                self.questions[self.q_difficulty].remove(self.question)
                self.question = {}

            return json.dumps({"correct": correct, "points": self.points, "finish_time": self.finish_time})

        elif command == 'CHECK_REGISTER':
            conn = sqlite3.connect(self.database)
            cur = conn.cursor()

            cur.execute('SELECT COUNT(*) FROM '+self._cfg_manager.get_value('romie_table')+' WHERE username = ?', (self.username,));
            count = cur.fetchone()[0]

            result = ''
            if count == 0 and not self._cfg_manager.get_value('romie_demo'):
                # This seems to work as expected.
                result = {'register': True, 'psycho': self._cfg_manager.get_value('romie_labpsico')}
            else:
                if self._cfg_manager.get_value('romie_demo') or self.get_psycho_points() > 0:
                    if self._cfg_manager.get_value('romie_demo') and count == 0:
                        self.register(self.username+"@weblab-demo.deusto.es", "Usuario", "Demo", "Escuela demo", 958305600, "Curso demo", 2)
                    self.finish_time = round(time.time()+self._cfg_manager.get_value('romie_time'), 3)
                    result = {'register': False, 'psycho': False, 'points': self.get_psycho_points()*1000, 'time': self.finish_time}
                else:
                    conn = sqlite3.connect(self.database)
                    cur = conn.cursor()
                    cur.execute('SELECT gender, birthday, grade FROM '+self._cfg_manager.get_value('romie_table')+' WHERE username = ?', (self.username, ))
                    result = cur.fetchone()
                    conn.close()
                    
                    self.finish_time = round(time.time()+self._cfg_manager.get_value('romie_time'), 3)
                    result = {'register': False, 'psycho': self._cfg_manager.get_value('romie_labpsico'), 'gender': result[0], 'time': self.finish_time, 'birthday': result[1], 'grade': result[2], 'user': self.username}

            conn.close()

            return json.dumps(result)

        elif command.startswith('REGISTER'):
            data = json.loads(command.split(' ', 1)[1])

            if (self.email_exists(data["email"])):
                return json.dumps({'error': 'email'})

            self.register(data["email"], data["name"], data["surname"], data["school"], data["bdate"], data['grade'], data['gender'])

            if not self._cfg_manager.get_value('romie_labpsico'):
                self.finish_time = round(time.time()+self._cfg_manager.get_value('romie_time'), 3)
                result = {'error': None, 'time': self.finish_time, 'points': self.points}
            else:
                result = {'error': None, 'gender': data['gender'], 'birthday': data['bdate'], 'grade': data['grade'], 'user': self.username}

            return json.dumps(result)

        elif command.startswith('PSYCHO'):
            psychopoints = (int) (command.split(' ')[1])
            self.points = psychopoints * 1000
            self.update_points()
            self.finish_time = round(time.time()+self._cfg_manager.get_value('romie_time'), 3)
            self.set_psycho_points(psychopoints)

            return json.dumps({'points': self.points, 'time': self.finish_time})
        elif command == 'FINISH':

            self.update_points()

            conn = sqlite3.connect(self.database)
            cur = conn.cursor()
            cur.execute('SELECT username, name, surname, school, points FROM '+self._cfg_manager.get_value('romie_table')+' ORDER BY points DESC LIMIT 10;')
            result = cur.fetchall()
            ranking = list()

            for user in result:
                current = (user[0] == self.username)
                ranking.append({"name":user[1], "surname":user[2], "school":user[3], "points":user[4], "current":current})

            conn.commit()
            conn.close()

            return json.dumps(ranking)

        return "ERROR"

    @Override(Experiment.Experiment)
    @logged("info")
    def do_dispose(self):
        """
        Callback to perform cleaning after the experiment ends.
        """
        if(self._cfg_manager.get_value('debug')):
            print "[RoMIE] do_dispose called"

        return "OK"

    def get_psycho_points(self):
        conn = sqlite3.connect(self.database)

        cur = conn.cursor()
        cur.execute('SELECT psycho FROM '+self._cfg_manager.get_value('romie_table')+' WHERE username = ?', (self.username,))
        psychopoints = (int) (cur.fetchone()[0])

        conn.close()
        return psychopoints

    def set_psycho_points(self, points):
        conn = sqlite3.connect(self.database)
        conn.execute('UPDATE '+self._cfg_manager.get_value('romie_table')+' SET psycho = ? WHERE username = ?', (points, self.username))
        conn.commit()
        conn.close()

    def update_points(self):
        """
        Update points in the database
        """
        conn = sqlite3.connect(self.database)

        cur = conn.cursor()
        cur.execute('SELECT points FROM '+self._cfg_manager.get_value('romie_table')+' WHERE username = ?', (self.username,))
        points = cur.fetchone()[0]

        if (points < self.points):
            conn.execute('UPDATE '+self._cfg_manager.get_value('romie_table')+' SET points = ? WHERE username = ?', (self.points, self.username))
            conn.commit()

        conn.close()

    def email_exists(self, email):
        """
        Check if email is already registered
        """
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM '+self._cfg_manager.get_value('romie_table')+' WHERE email = ?', (email,));
        count = cur.fetchone()[0]
        conn.close()

        return count > 0

    def register(self, email, name, surname, school, bdate, grade, gender):
        conn = sqlite3.connect(self.database)
        conn.execute('INSERT INTO '+self._cfg_manager.get_value('romie_table')+' values (?,?,?,?,?,?,?,?,?,?)',
            (self.username, email, name, surname, school, bdate, grade, gender, False, 0))
        conn.commit()
        conn.close()
