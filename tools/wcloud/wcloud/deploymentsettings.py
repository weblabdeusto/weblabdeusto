"""
This file contains the default deployment settings.

Most of these parameters are automatically overriden when creating a new instance,
and passed to the weblab-admin script.
"""


from weblab.admin.script import Creation


APACHE_CONF_NAME = 'apache.conf'
MIN_PORT = 14000

DEFAULT_DEPLOYMENT_SETTINGS = {
    Creation.DB_ENGINE: 'mysql',
    Creation.COORD_ENGINE: 'redis',
    Creation.COORD_REDIS_DB: 0,                    # --coordination-redis-db=COORD_REDIS_DB
    Creation.COORD_REDIS_PORT: 6379,               # --coordination-redis-port=PORT
    Creation.ADMIN_USER: 'admin',              # --admin-user=admin
    Creation.ADMIN_NAME: 'Administrator',              #  --admin-name=(lo que diga)
    Creation.ADMIN_PASSWORD: 'password',          # --admin-password=(lo que diga)
    Creation.ADMIN_MAIL: 'admin@admin.com',              # --admin-mail=(lo que diga)
    Creation.START_PORTS: '10000',             # --start-port=10000
    Creation.SYSTEM_IDENTIFIER: 'University of Deusto',       # -i (nombre de la uni, puede tener espacios)
    Creation.SERVER_HOST: 'weblab.deusto.es',      # --server-host=(de settings)
    Creation.ENTITY_LINK: 'http://www.deusto.es/', # --entity-link= http://www.deusto.es/
    Creation.CORES: 3, 
    Creation.ADD_FEDERATED_LOGIC : True,
    Creation.ADD_FEDERATED_VISIR : True,
    Creation.ADD_FEDERATED_SUBMARINE : True,
}
