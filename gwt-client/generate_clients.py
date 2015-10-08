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

# 
# Native clients
# 
experiment_clients['blank'] = {
        "parameters": {
            "experiment.info.description": {
                "type": "string", 
                "description": "Description message"
            }, 
            "html": {
                "type": "string", 
                "description": "HTML contents"
            }, 
            "experiment.info.link": {
                "type": "string", 
                "description": "Link to point in the information"
            }, 
            "experiment.reserve.button.shown": {
                "type": "bool", 
                "description": "Show the reserve button or not"
            }, 
            "experiment.picture": {
                "type": "string", 
                "description": "Path to the experiment pictures"
            }
        }
    }

# Backwards compatibility
experiment_clients['blank-no-mobile'] = experiment_clients['blank-limited-mobile'] = experiment_clients['blank']

experiment_clients['redirect'] = {
        "parameters": {
            "external.width": {
                "type": "string", 
                "description": "If popup or iframe,  width"
            }, 
            "external.height": {
                "type": "string", 
                "description": "If popup or iframe,  height"
            }, 
            "experiment.reserve.button.shown": {
                "type": "bool", 
                "description": "Show the reserve button or not"
            }, 
            "experiment.info.description": {
                "type": "string", 
                "description": "Description message"
            }, 
            "link.presentation": {
                "type": "string", 
                "description": "Link presentation (redirection, iframe, popup)"
            }, 
            "experiment.info.link": {
                "type": "string", 
                "description": "Link to point in the information"
            }, 
            "experiment.picture": {
                "type": "string", 
                "description": "Path to the experiment pictures"
            }
        }
    }

experiment_clients['js'] = {
        "parameters": {
            "builtin": {
                "type": "bool", 
                "description": "If active, it means that it comes with WebLab-Deusto; otherwise it takes the HTML file from the 'pub' directory"
            }, 
            "provide.file.upload": {
                "type": "bool", 
                "description": "Provide upload file"
            }, 
            "html.file": {
                "type": "string", 
                "description": "HTML file"
            }, 
            "experiment.reserve.button.shown": {
                "type": "bool", 
                "description": "Show the reserve button or not"
            }, 
            "page.footer": {
                "type": "string", 
                "description": "Footer of the application (below the application loaded, defaultValue)"
            }, 
            "experiment.info.description": {
                "type": "string", 
                "description": "Description message"
            }, 
            "cssHeight": {
                "type": "string", 
                "description": "CSS height"
            }, 
            "experiment.info.link": {
                "type": "string", 
                "description": "Link to point in the information"
            }, 
            "message": {
                "type": "string", 
                "description": "Message to be displayed"
            }, 
            "cssWidth": {
                "type": "string", 
                "description": "CSS width"
            }, 
            "experiment.picture": {
                "type": "string", 
                "description": "Path to the experiment pictures"
            }
        }
    }

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
