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
    "laboratory:main_instance@main_machine" : {
            "exp1|dummy1|Dummy experiments"        : "dummy1@dummy1",
            "exp1|dummy2|Dummy experiments"        : "dummy1@dummy2",
        }
}

core_scheduling_systems = {
        "dummy1"      : ("PRIORITY_QUEUE", {}),
        "dummy2"      : ("PRIORITY_QUEUE", {}),
    }

core_universal_identifier       = 'b9bbe9e2-ea14-11e0-bd1d-00216a5807c8'
core_universal_identifier_human = "Provider 2"

core_server_url = 'http://localhost/weblab/'
