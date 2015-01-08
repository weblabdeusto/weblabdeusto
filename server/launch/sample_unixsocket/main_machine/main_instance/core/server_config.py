########################################
# User Processing Server configuration #
########################################

core_session_type = 'Memory'

core_coordinator_db_username = 'weblab'
core_coordinator_db_password = 'weblab'

weblab_db_username = 'weblab'
weblab_db_password = 'weblab'

core_coordinator_laboratory_servers = {
    "laboratory:main_instance@main_machine" : {
            "exp1|ud-dummy|Dummy experiments"        : "dummy@dummy",
        }
}

core_scheduling_systems = {
        "dummy"      : ("PRIORITY_QUEUE", {}),
    }

##############################
# RemoteFacade configuration #
##############################

core_facade_soap_service_name = '/weblab/soap/'


core_facade_bind      = ''
core_facade_port        = 18345



core_universal_identifier       = 'da2579d6-e3b2-11e0-a66a-00216a5807c8'
core_universal_identifier_human = 'server at university X'

core_server_url = 'http://localhost/weblab/'

weblab_db_username = 'weblab'
weblab_db_password = 'weblab'

##############################
# RemoteFacade configuration #
##############################

login_facade_soap_service_name = '/weblab/login/soap/'




