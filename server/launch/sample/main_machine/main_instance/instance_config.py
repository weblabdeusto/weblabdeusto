#########################
# General configuration #
#########################

server_hostaddress = 'weblab.deusto.es'
server_admin       = 'weblab@deusto.es'

################################
# Admin Notifier configuration #
################################

mail_notification_enabled = False
mail_server_host          = 'rigel.deusto.es'
mail_server_use_tls       = 'yes'
mail_server_helo          = server_hostaddress
mail_notification_sender  = 'weblab@deusto.es'
mail_notification_subject = '[WebLab] CRITICAL ERROR!'

##########################
# Sessions configuration #
##########################

session_mysql_username = 'weblab'
session_mysql_password = 'weblab'

session_locker_mysql_username = 'weblab'
session_locker_mysql_password = 'weblab'