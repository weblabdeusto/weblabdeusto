xilinx_use_jtag_blazer_to_program = False


#########################
# General configuration #
#########################

server_hostaddress        = 'weblab.deusto.es'
server_admin              = 'weblab@deusto.es'

###############################
# Mail Notifier configuration #
###############################

mail_notification_enabled = False
mail_server_host          = 'rigel.deusto.es'
mail_server_use_tls       = 'yes'
mail_server_helo          = server_hostaddress
mail_notification_sender  = 'weblab@deusto.es'
mail_notification_subject = '[WebLab] CRITICAL ERROR!'

###################################
# Sessions database configuration #
###################################

session_mysql_host     = 'localhost'
session_mysql_db_name  = 'WebLabSessions'
session_mysql_username = 'wl_session_user'
session_mysql_password = 'wl_session_user_password'

##########################################
# Sessions locker database configuration #
##########################################

session_locker_mysql_host     = 'localhost'
session_locker_mysql_db_name  = 'WebLabSessions'
session_locker_mysql_username = 'wl_session_user'
session_locker_mysql_password = 'wl_session_user_password'

########################
# Loader configuration #
########################

loader_check_configuration_syntax = True
loader_xsd_path                   = "WebLabSkel/lib/schemas/"

#############################
# Experiments configuration #
#############################

core_experiment_poll_time = 15 # seconds

####################################
# Coordinator Server configuration #
####################################

coordinator_server_session_type = 'Memory'

