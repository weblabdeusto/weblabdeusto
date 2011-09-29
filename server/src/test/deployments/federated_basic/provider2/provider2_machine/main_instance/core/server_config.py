core_store_students_programs      = False
core_store_students_programs_path = 'files_stored'
core_experiment_poll_time         = 350 # seconds

# Ports

core_facade_soap_port   = 30123
core_facade_xmlrpc_port = 39345
core_facade_json_port   = 38345

admin_facade_json_port   = 38545

core_web_facade_port   = 39745

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

core_scheduling_systems = {
        "dummy1"      : ("PRIORITY_QUEUE", {}),
        "dummy4"      : ("PRIORITY_QUEUE", {}),
    }

core_server_url = 'http://localhost/weblab/'
