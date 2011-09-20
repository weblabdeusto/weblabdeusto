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

core_coordinator_laboratory_servers = {
            "laboratory:lab_and_experiment@main_machine" : { "exp1|ud-dummy|Dummy experiments" : "dummy@ud-dummy" }
        }

core_scheduling_systems = {
        "ud-fpga"    : ("PRIORITY_QUEUE", {}),
        "ud-pld"     : ("PRIORITY_QUEUE", {}),
        "ud-gpib"    : ("PRIORITY_QUEUE", {}),
        "ud-pic"     : ("PRIORITY_QUEUE", {}),
        "ud-dummy"   : ("PRIORITY_QUEUE", {}),
        "ud-logic"   : ("PRIORITY_QUEUE", {}),
        "flashdummy" : ("PRIORITY_QUEUE", {}),
        "javadummy"  : ("PRIORITY_QUEUE", {}),
        "visirtest"  : ("PRIORITY_QUEUE", {}),
    }


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
db_prefix        = "wl_"

core_universal_identifier       = 'da2579d6-e3b2-11e0-a66a-00216a5807c8'
core_universal_identifier_human = 'Server X at Sample University'
