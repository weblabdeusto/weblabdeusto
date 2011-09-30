core_store_students_programs      = False
core_store_students_programs_path = 'files_stored'
core_experiment_poll_time         = 350 # seconds

# Ports

core_facade_soap_port   = 10123
core_facade_xmlrpc_port = 19345
core_facade_json_port   = 18345

admin_facade_json_port   = 18545

core_web_facade_port   = 19745

# Scheduling

core_coordinator_db_username = 'weblab'
core_coordinator_db_password = 'weblab'

core_coordinator_laboratory_servers = {
    "laboratory:main_instance@consumer_machine" : {
            "exp1|dummy1|Dummy experiments"        : "dummy1@dummy1",
            "exp1|dummy2|Dummy experiments"        : "dummy1@dummy2",
        }
}

core_coordinator_external_servers = {
    'dummy3@Dummy experiments'  : [ 'dummy3' ]
}

core_scheduling_systems = {
        "dummy1"      : ("PRIORITY_QUEUE", {}),
        "dummy2"      : ("PRIORITY_QUEUE", {}),
        "dummy3"      : ("EXTERNAL_WEBLAB_DEUSTO", { 
                                    'baseurl' : 'http://127.0.0.1:28345/weblab/', 
                                    'login_baseurl' : 'http://127.0.0.1:28645/weblab/',
                                    'username' : 'consumer1', 
                                    'password' : 'password',
                            }),
    }

core_server_url = 'http://localhost/weblab/'
