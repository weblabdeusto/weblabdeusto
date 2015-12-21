server_admin = 'weblab@deusto.es'
debug_mode   = True
flask_debug = True
vt_use_visir_php = False

# db_engine = 'sqlite'
db_engine = 'mysql'
core_coordinator_db_engine     = db_engine
session_sqlalchemy_engine      = db_engine
session_lock_sqlalchemy_engine = db_engine

core_coordination_impl = 'redis'
core_coordinator_clean = True
login_default_groups_for_external_users = ['Demos','Course 2008/09','Federated users']
