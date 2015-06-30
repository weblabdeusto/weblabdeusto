from __future__ import print_function, unicode_literals
core_store_students_programs      = False
core_store_students_programs_path = 'files_stored'
core_experiment_poll_time         = 350 # seconds

# Ports
core_facade_port   = 18345



core_facade_server_route = 'consumer-route'

# Will only work in JSON in this config file :-(
core_server_url = 'http://127.0.0.1:%s/weblab/' % core_facade_port

# Scheduling

core_coordinator_db_username = 'weblab'
core_coordinator_db_password = 'weblab'

core_coordinator_laboratory_servers = {
    "laboratory:main_instance@consumer_machine" : {
            "exp1|dummy1|Dummy experiments"        : "dummy1@dummy1_local",
            "exp1|dummy2|Dummy experiments"        : "dummy1@dummy2",
        }
}

core_coordinator_external_servers = {
    'dummy1@Dummy experiments'  : [ 'dummy1_external' ],
    'dummy3@Dummy experiments'  : [ 'dummy3' ],
    'dummy4@Dummy experiments'  : [ 'dummy4' ],
}

_provider1_scheduling_config = ("EXTERNAL_WEBLAB_DEUSTO", {
                                    'baseurl' : 'http://127.0.0.1:28345/weblab/',
                                    'username' : 'consumer1',
                                    'password' : 'password',
                                    'experiments_map' : {'dummy3@Dummy experiments' : 'dummy3_with_other_name@Dummy experiments'}
                            })

core_scheduling_systems = {
        "dummy1_local"    : ("PRIORITY_QUEUE", {}),
        "dummy2"          : ("PRIORITY_QUEUE", {}),
        "dummy3"          : _provider1_scheduling_config,
        "dummy4"          : _provider1_scheduling_config,
        "dummy1_external" : _provider1_scheduling_config,
    }

core_weblabdeusto_federation_retrieval_period = 0.1

