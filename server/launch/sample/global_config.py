server_admin = 'weblab@deusto.es'
debug_mode   = True
flask_debug = True

# db_engine = 'sqlite'
db_engine = 'mysql'
core_coordinator_db_engine     = db_engine
session_sqlalchemy_engine      = db_engine
session_lock_sqlalchemy_engine = db_engine

core_coordination_impl = 'redis'
core_coordinator_clean = True
