########################################
# User Processing Server configuration #
########################################

core_session_type = 'Memory'

core_coordinator_db_username = 'weblab'
core_coordinator_db_password = 'weblab'

weblab_db_username = 'weblab'
weblab_db_password = 'weblab'

core_coordinator_laboratory_servers   = [
    "laboratory1:main_instance@main_machine;exp1|ud-fpga|FPGA experiments",
    "laboratory1:main_instance@main_machine;exp1|ud-pld|PLD experiments",
    "laboratory1:main_instance@main_machine;exp1|ud-gpib|GPIB experiments",
    "laboratory1:main_instance@main_machine;exp1|ud-pic|PIC experiments",
    "laboratory1:main_instance@main_machine;exp1|ud-dummy|Dummy experiments",
]

##########################
# Database configuration #
##########################


core_db_users_student_read_username         = 'wl_student_read'
core_db_users_student_read_password         = 'wl_student_read_password'
core_db_users_student_write_username        = 'wl_student_write'
core_db_users_student_write_password        = 'wl_student_write_password'
core_db_users_professor_read_username       = 'wl_prof_read'
core_db_users_professor_read_password       = 'wl_prof_read_password'
core_db_users_professor_write_username      = 'wl_prof_write'
core_db_users_professor_write_password      = 'wl_prof_write_password'
core_db_users_administrator_read_username   = 'wl_admin_read'
core_db_users_administrator_read_password   = 'wl_admin_read_password'
core_db_users_administrator_write_username  = 'wl_admin_write'
core_db_users_administrator_write_password  = 'wl_admin_write_password'
core_db_users_externalentity_read_username  = 'wl_exter_read'
core_db_users_externalentity_read_password  = 'wl_exter_read_password'
core_db_users_externalentity_write_username     = 'wl_exter_write'
core_db_users_externalentity_write_password     = 'wl_exter_write_password'

db_driver        = "MySQLdb"
db_host          = "localhost"
db_database = "WebLabTests"
db_prefix        = ""

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

admin_facade_json_port        = 18545

