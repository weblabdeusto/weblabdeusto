from __future__ import print_function, unicode_literals
core_store_students_programs      = False
core_store_students_programs_path = 'files_stored'
core_experiment_poll_time         = 350 # seconds

# Ports
core_facade_port   = 38345


core_facade_server_route = 'provider2-route'

core_server_url = 'http://127.0.0.1:%s/weblab/' % core_facade_port

# Scheduling

core_coordinator_db_name     = 'WebLabCoordination3'
core_coordinator_db_username = 'weblab'
core_coordinator_db_password = 'weblab'

core_coordinator_laboratory_servers = {
    "laboratory:main_instance@provider2_machine" : {
            "exp1|dummy1|Dummy experiments"        : "dummy1@dummy1",
            "exp1|dummy4|Dummy experiments"        : "dummy4@dummy4",
        }
}

core_coordinator_external_servers = {
    'dummy1@Dummy experiments'  : [ 'dummy1_external' ],
}

_provider1_scheduling_config = ("EXTERNAL_WEBLAB_DEUSTO", {
                                    'baseurl' : 'http://127.0.0.1:28345/weblab/',
                                    'username' : 'provider2',
                                    'password' : 'password',
                            })

core_scheduling_systems = {
        "dummy1"          : ("PRIORITY_QUEUE", {}),
        "dummy4"          : ("PRIORITY_QUEUE", {}),
        "dummy1_external" : _provider1_scheduling_config,
    }

core_weblabdeusto_federation_retrieval_period = 0.1
