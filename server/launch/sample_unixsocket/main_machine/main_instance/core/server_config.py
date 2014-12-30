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

core_facade_soap_bind       = ''
core_facade_soap_port         = 10123
core_facade_soap_service_name = '/weblab/soap/'

core_facade_xmlrpc_bind    = ''
core_facade_xmlrpc_port      = 19345

core_facade_json_bind      = ''
core_facade_json_port        = 18345

core_web_facade_port   = 19745

admin_facade_json_port        = 18545

core_universal_identifier       = 'da2579d6-e3b2-11e0-a66a-00216a5807c8'
core_universal_identifier_human = 'server at university X'

core_server_url = 'http://localhost/weblab/'

weblab_db_username = 'weblab'
weblab_db_password = 'weblab'

##############################
# RemoteFacade configuration #
##############################

login_facade_soap_bind       = ''
login_facade_soap_port         = 10623
login_facade_soap_service_name = '/weblab/login/soap/'

login_facade_xmlrpc_bind    = ''
login_facade_xmlrpc_port      = 19645

login_facade_json_bind      = ''
login_facade_json_port        = 18645

login_web_facade_port = 18745

