import os
from weblab.admin.script import Creation

DIR_BASE = os.path.expanduser(os.path.join('~', '.weblab')) # home path
APACHE_CONF_NAME = 'apache.conf'
MIN_PORT = 10000
APACHE_RELOAD_SERVICE = 'http://127.0.0.1:22110'
CUSTOM_DEPLOYMENT_SETTINGS = {}

DEFAULT_DEPLOYMENT_SETTINGS = {
    Creation.COORD_ENGINE: 'redis',
    Creation.COORD_REDIS_DB: 0,
    Creation.COORD_REDIS_PORT: 6379,
    Creation.BASE_URL: 'CHANGE_ME',
    Creation.DB_ENGINE: 'mysql',
    Creation.DB_NAME: 'CHANGE_ME', # --db-name=WebLabDeployment(1)
    Creation.DB_USER: 'root', # --db-user=(de settings)
    Creation.DB_PASSWD: 'larrakoetxea', # --db-passwd=(de settings)
    Creation.ADMIN_USER: 'CHANGE_ME', # --admin-user=admin
    Creation.ADMIN_NAME: 'CHANGE_ME', #  --admin-name=(lo que diga)
    Creation.ADMIN_PASSWORD: 'CHANGE_ME', # --admin-password=(lo que diga)
    Creation.ADMIN_MAIL: 'CHANGE_ME', # --admin-mail=(lo que diga)
    Creation.START_PORTS: 'CHANGE_ME', # --start-port=10000
    Creation.SYSTEM_IDENTIFIER: 'CHANGE_ME', # -i (nombre de la uni, puede tener espacios)
    Creation.SERVER_HOST: 'weblab.deusto.es', # --server-host=(de settings)
    Creation.ENTITY_LINK: 'http://www.deusto.es/', # --entity-link= http://www.deusto.es/
    Creation.CORES: 3, 

}

DEFAULT_DEPLOYMENT_SETTINGS.update(CUSTOM_DEPLOYMENT_SETTINGS)
