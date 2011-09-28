core_store_students_programs      = False
core_store_students_programs_path = 'files_stored'
core_experiment_poll_time         = 350 # seconds

# Ports

core_facade_soap_port   = 20123
core_facade_xmlrpc_port = 29345
core_facade_json_port   = 28345

admin_facade_json_port   = 28545

core_web_facade_port   = 29745

# Scheduling

core_coordinator_db_name     = 'WebLabCoordination2'
core_coordinator_db_username = 'weblab'
core_coordinator_db_password = 'weblab'

core_coordinator_laboratory_servers = {
    "laboratory:main_instance@main_machine" : {
            "exp1|dummy1|Dummy experiments"        : "dummy1@dummy1",
            "exp1|dummy3|Dummy experiments"        : "dummy3@dummy3",
        }
}

core_scheduling_systems = {
        "dummy1"      : ("PRIORITY_QUEUE", {}),
        "dummy3"      : ("PRIORITY_QUEUE", {}),
    }

core_universal_identifier       = 'c7ab5d9e-ea14-11e0-bd1d-00216a5807c8'
core_universal_identifier_human = 'Provider 1'

core_server_url = 'http://localhost/weblab/'
