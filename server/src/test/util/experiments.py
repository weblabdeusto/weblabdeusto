from __future__ import print_function, unicode_literals
import json

import weblab.core.coordinator.coordinator as Coordinator
import weblab.experiment.level as level

from weblab.experiment.experiment import Experiment

class StorageExperiment(Experiment):
    def __init__(self, coord_address, locator, config, *args, **kwargs):
        super(StorageExperiment, self).__init__(*args, **kwargs)
        self.commands = []

    def do_start_experiment(self, client_initial_data, server_initial_data):
        return "{}"

    def do_get_api(self):
        return level.level_2

    def do_send_command_to_device(self, command):
        self.commands.append(command)
        return command

    def do_send_file_to_device(self, file_content, file_info):
        return "ack"

    def clear(self):
        self.commands = []

    def do_dispose(self):
        return json.dumps({ Coordinator.FINISH_FINISHED_MESSAGE : True, Coordinator.FINISH_DATA_MESSAGE : ""})

