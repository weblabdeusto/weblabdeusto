#######################
# Login configuration #
#######################

weblab_db_username = 'weblab'
weblab_db_password = 'weblab'

########################################
# User Processing Server configuration #
########################################

core_session_type = 'Memory'

core_coordinator_db_username = 'weblab'
core_coordinator_db_password = 'weblab'

core_scheduling_systems = {
        "dummy"   : ("PRIORITY_QUEUE", {}),
    }

core_coordinator_laboratory_servers = {
            "laboratory:lab_and_experiment@main_machine" : { 
                "exp1|ud-dummy|Dummy experiments" : "dummy@dummy" 
            }
        }

##########################
# Database configuration #
##########################


db_host     = "localhost"
db_database = "WebLabTests"

core_universal_identifier       = 'da2579d6-e3b2-11e0-a66a-00216a5807c8'
core_universal_identifier_human = 'server X at Sample University'

core_server_url = 'http://localhost/weblab/'
