import os


DIR_BASE = os.path.expanduser(os.path.join('~', '.weblab')) # home path
APACHE_CONF_NAME = 'apache.conf'

CUSTOM_DEPLOYMENT_SETTINGS = {}

DEFAULT_DEPLOYMENT_SETTINGS = {
    'COORD_ENGINE ': 'redis',
    'COORD_REDIS_DB': 0,
    'COORD_REDIS_PORT': 6379,
    'BASE_URL': 'CHANGE_ME',
    'DB_ENGINE': 'mysql',
    'DB_NAME': 'CHANGE_ME', # --db-name=WebLabDeployment(1)
    'DB_USER': 'CHANGE_ME', # --db-user=(de settings)
    'DB_PASSWD': 'CHANGE_ME', # --db-passwd=(de settings)
    'ADMIN_USER': 'CHANGE_ME', # --admin-user=admin
    'ADMIN_NAME': 'CHANGE_ME', #  --admin-name=(lo que diga)
    'ADMIN_PASSWORD': 'CHANGE_ME', # --admin-password=(lo que diga)
    'ADMIN_MAIL': 'CHANGE_ME', # --admin-mail=(lo que diga)
    'START_PORTS': 'CHANGE_ME', # --start-port=10000
    'SYSTEM_IDENTIFIER': 'CHANGE_ME', # -i (nombre de la uni, puede tener espacios)
    'SERVER_HOST': 'CHANGE_ME', # --server-host=(de settings)
    'ENTITY_LINK': 'http://www.deusto.es/', # --entity-link= http://www.deusto.es/
    'CORES': 3, 

}

DEFAULT_DEPLOYMENT_SETTINGS.update(CUSTOM_DEPLOYMENT_SETTINGS)
