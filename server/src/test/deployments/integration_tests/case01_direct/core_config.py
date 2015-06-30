from __future__ import print_function, unicode_literals
core_store_students_programs      = False
core_store_students_programs_path = 'files_stored'
core_experiment_poll_time         = 350 # seconds

# Ports
core_facade_port   = 18341


core_facade_server_route = 'testing-route'

core_server_url = 'http://127.0.0.1:%s/weblab/' % core_facade_port

# Scheduling

core_coordinator_db_name     = 'WebLabCoordination'
core_coordinator_db_username = 'weblab'
core_coordinator_db_password = 'weblab'

core_coordinator_laboratory_servers = {
    "mylab:myprocess@myhost" : {
            "exp1|dummy1|Dummy experiments"        : "dummy1@dummy1",
            "exp1|dummy2|Dummy experiments"        : "dummy2@dummy2",
        }
}

core_coordinator_external_servers = {}

core_scheduling_systems = {
        "dummy1"          : ("PRIORITY_QUEUE", {}),
        "dummy2"          : ("PRIORITY_QUEUE", {}),
    }
