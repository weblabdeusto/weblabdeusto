#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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
#
from __future__ import print_function, unicode_literals

import hashlib
import time as time_module
import weblab.experiment.util as ExperimentUtil

import weblab.configuration_doc as configuration_doc

def _get_time_in_str():
    cur_time = time_module.time()
    s = time_module.strftime('%Y_%m_%d___%H_%M_%S_',time_module.gmtime(cur_time))
    millis = int((cur_time - int(cur_time)) * 1000)
    return s + str(millis)


class FileStorer(object):

    def __init__(self, cfg_manager, reservation_id, time_module = time_module):
        self._cfg_manager    = cfg_manager
        self.time_module     = time_module
        self._reservation_id = reservation_id

    def _utc_timestamp(self):
        return self.time_module.time()

    def store_file(self, file_content, file_info):
        import weblab.data.experiments as Experiments

        # TODO: this is a very dirty way to implement this. Anyway until the good approach is taken, this will store the students programs
        # TODO: there should be two global variables: first, if store_student_files is not activated, do nothing.
        #       but, if store_student_files is activated, it should check that for a given experiment, they should be stored or not.
        #       For instance, I may want to store GPIB experiments but not FPGA experiments. Indeed, this should be stored in the db
        #       in the permission of the student/group with the particular experiment, with a default value to True.
        should_i_store = self._cfg_manager.get_doc_value(configuration_doc.CORE_STORE_STUDENTS_PROGRAMS)
        timestamp_before   = self._utc_timestamp()
        if should_i_store:
            # TODO not tested
            if isinstance(file_content, unicode):
                file_content_encoded = file_content.encode('utf8')
            else:
                file_content_encoded = file_content
            deserialized_file_content = ExperimentUtil.deserialize(file_content_encoded)
            storage_path = self._cfg_manager.get_doc_value(configuration_doc.CORE_STORE_STUDENTS_PROGRAMS_PATH)
            relative_file_path = _get_time_in_str() + '_' + self._reservation_id
            sha_obj            = hashlib.new('sha')
            sha_obj.update(deserialized_file_content)
            file_hash          = sha_obj.hexdigest()

            where = storage_path + '/' + relative_file_path
            f = open(where,'w')
            f.write(deserialized_file_content)
            f.close()

            return Experiments.FileSent(relative_file_path, "{sha}%s" % file_hash, timestamp_before, file_info = file_info)
        else:
            return Experiments.FileSent("<file not stored>","<file not stored>", timestamp_before, file_info = file_info)

