########################################
# User Processing Server configuration #
########################################

core_session_type = 'Memory'

core_coordinator_db_username = 'weblab'
core_coordinator_db_password = 'weblab'

weblab_db_username = 'weblab'
weblab_db_password = 'weblab'

core_coordinator_laboratory_servers = [
                "laboratory1:main_instance@main_machine;exp1|ud-dummy|Dummy experiments",
                "laboratory1:main_instance@main_machine;exp1|javadummy|Dummy experiments"
        ]


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

