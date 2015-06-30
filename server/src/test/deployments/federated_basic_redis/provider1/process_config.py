from __future__ import print_function, unicode_literals
weblab_db_force_engine_creation = True

core_universal_identifier       = 'c7ab5d9e-ea14-11e0-bd1d-00216a5807c8'
core_universal_identifier_human = 'Provider 1'

db_database = "WebLabTests2"
weblab_db_username = 'weblab'
weblab_db_password = 'weblab'

server_admin = 'weblab@deusto.es'
debug_mode   = True

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
