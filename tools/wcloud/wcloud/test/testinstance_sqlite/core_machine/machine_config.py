# It must be here to retrieve this information from the dummy
core_universal_identifier       = 'f2ce65bb-8543-47c1-82bf-44fe191551bb'
core_universal_identifier_human = 'Generic system; not identified'

db_engine          = 'sqlite'
db_host            = 'localhost'
db_port            = None # None for default
db_database        = 'WebLab'
weblab_db_username = 'weblab'
weblab_db_password = 'weblab'

debug_mode   = True

#########################
# General configuration #
#########################

server_hostaddress = 'localhost'
server_admin       = ''

################################
# Admin Notifier configuration #
################################

mail_notification_enabled = False

##########################
# Sessions configuration #
##########################

core_session_type = 'Memory'

# session_sqlalchemy_engine   = 'sqlite'
# session_sqlalchemy_host     = 'localhost'
# session_sqlalchemy_username = ''
# session_sqlalchemy_password = ''

# session_lock_sqlalchemy_engine   = 'sqlite'
# session_lock_sqlalchemy_host     = 'localhost'
# session_lock_sqlalchemy_username = ''
# session_lock_sqlalchemy_password = ''

# session_redis_host = 'localhost'
# session_redis_port = 6379
# core_session_pool_id = 1
# core_alive_users_session_pool_id = 1

##############################
# Core generic configuration #
##############################
core_store_students_programs      = False
core_store_students_programs_path = 'files_stored'
core_experiment_poll_time         = 350 # seconds

core_server_url = 'http://localhost/weblab/'

############################
# Scheduling configuration #
############################

core_coordination_impl = 'sqlalchemy'

# coordinator_redis_db       = None
# coordinator_redis_password = None
# coordinator_redis_port     = None

core_coordinator_db_name      = 'WebLabCoordination'
core_coordinator_db_engine    = 'sqlite'
core_coordinator_db_host      = 'localhost'
core_coordinator_db_username  = 'weblab'
core_coordinator_db_password  = 'weblab'

core_coordinator_laboratory_servers = {
    'laboratory1:laboratory1@core_machine' : {
            'exp1|dummy|Dummy experiments'        : 'dummy1@dummy',
        },

}

core_coordinator_external_servers = {
    'external-robot-movement@Robot experiments'   : [ 'robot_external' ],
}

weblabdeusto_federation_demo = ('EXTERNAL_WEBLAB_DEUSTO', {
                                    'baseurl' : 'https://www.weblab.deusto.es/weblab/',
                                    'login_baseurl' : 'https://www.weblab.deusto.es/weblab/',
                                    'username' : 'weblabfed',
                                    'password' : 'password',
                                    'experiments_map' : {'external-robot-movement@Robot experiments' : 'robot-movement@Robot experiments'}
                            })

core_scheduling_systems = {
        'dummy'            : ('PRIORITY_QUEUE', {}),
        'robot_external'   : weblabdeusto_federation_demo,
    }

