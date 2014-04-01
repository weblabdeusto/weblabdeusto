import os

"""
This file contains a sample configuration file. All the applications
use a environment variable called WCLOUD_SETTINGS which must point to
a valid Python file. If this file is found, those variables located there
will replace these variables. So if you only need to establish passwords,
reCAPTCHA configuration, etc., you only need to put the file with those 
variables. However, for development that's not required.
"""

#################################
# 
# Flask general configuration
# 
DEBUG = True
SECRET_KEY = os.urandom(32)

ADMIN_MAIL = 'weblab@deusto.es'

# If you want to support reCAPTCHA, set this to
# True and provide the credentials
RECAPTCHA_ENABLED = False
RECAPTCHA_PUBLIC_KEY  = 'public key'
RECAPTCHA_PRIVATE_KEY = 'private key'


MAIL_CONFIRMATION_ENABLED = False


# 
# We have to use multiple Redis servers (Redis supports by default up to 16 databases,
# and adding more may affect performance)
# 
REDIS_START_PORT=6379 + 1 # So we don't use the 6379
REDIS_DBS_PER_PORT=16

##########################
# 
# DB configuration:
# 
# Both MySQL and PostgreSQL are supported
# 
DB_NAME = 'wcloud'
DB_HOST = '127.0.0.1'

# 
# PostgreSQL
# DB_PORT = 5432
# DB_USERNAME = 'postgres'
# DB_PASSWORD = 'postgres'
# 
# MySQL
# 
DB_PORT = 3306
DB_USERNAME = 'weblab'
DB_PASSWORD = 'weblab'

# 
# PostgreSQL
# SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://%s:%s@%s:%d/%s' % (DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME )
# 
# MySQL
# 
SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s:%d/%s' % (DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME )

#############################
#
# Services configuration
# 
WEBLAB_STARTER_PORT  = 1663
APACHE_RELOADER_PORT = 1662
TASK_MANAGER_PORT    = 1661

PUBLIC_URL = 'http://localhost'
DIR_BASE = os.path.expanduser(os.path.join('~', '.weblab')) # home path
ADMINISTRATORS = ('pablo.orduna@deusto.es',)
