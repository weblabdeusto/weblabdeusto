#!/usr/bin/env python

import os
import glob
import json
from collections import OrderedDict

jar_files = ':'.join(glob.glob("external/gwt/*.jar"))

BIN_DIR = 'war/WEB-INF/classes/:%s' % jar_files
SUMMARY_TXT = 'clients_summary.txt'
JSON_FILE = '../server/src/weblab/clients.json'

os.system("java -classpath %s es.deusto.weblab.server.ClientSummaryGenerator" % BIN_DIR)

pending_lines = []

experiment_clients = OrderedDict()
    # 'client_id' : {
    #   'parameters' : {
    #      'parameter1' : {
    #          'type' : 'str',
    #          'description' : 'Foo bar',
    #      }
    #   }
    # }


def process_last_type():
    if pending_lines:
        experiment_client_type = pending_lines[0]
        if not experiment_client_type.startswith('Type::::'):
            raise Exception("Expected Type::::, found: %s" % experiment_client_type)
        experiment_client_type = experiment_client_type[len('Type::::'):].strip()

        parameters = {}

        for parameter_line in pending_lines[1:]:
            if not parameter_line.startswith('Parameter::::'):
                raise Exception("Expected Parameter::::, found: %s" % parameter_line)
            parameter_data = parameter_line.strip().split('::::')
            if len(parameter_data) != 4:
                raise Exception("Expected four blocks in parameter. Found: %s" % parameter_data)

            _, name, parameter_type, description = parameter_data

            parameters[name] = {
                'type' : parameter_type,
                'description' : description
            }
        
        experiment_clients[experiment_client_type] = {
                'parameters' : parameters
            }


for line in open(SUMMARY_TXT):
    if line.startswith("Type::::"):
        process_last_type()
        pending_lines = []
    pending_lines.append(line)

process_last_type()

os.remove(SUMMARY_TXT)

json.dump(experiment_clients, open(JSON_FILE, 'w'), indent = 4)

print "%s updated" % JSON_FILE
