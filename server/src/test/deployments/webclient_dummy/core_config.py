core_store_students_programs      = False
core_store_students_programs_path = 'files_stored'
core_experiment_poll_time         = 350 # seconds

# Used for testing: do not start the real server
dont_start = True
# Use the flask server
flask_debug = True

# Ports
core_facade_port   = 18340


core_facade_server_route = 'webclient-route'

core_server_url = 'http://127.0.0.1:%s/weblab/' % core_facade_port

# Scheduling

core_coordination_impl       = 'redis'
coordinator_redis_db         = 1

core_coordinator_laboratory_servers = {
    "mylab:myprocess@myhost" : {
            "exp1|dummy1|Dummy experiments"        : "dummy1@dummy1",
        }
}

core_coordinator_external_servers = {}

core_scheduling_systems = {
        "dummy1"          : ("PRIORITY_QUEUE", {}),
    }
