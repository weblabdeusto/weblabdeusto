from collections import namedtuple

NO_DEFAULT = object()
ANY_TYPE   = object()

_Argument = namedtuple('Argument', 'category type default message')

_sorted_variables = []


######################################
# 
# COMMON
# 

COMMON = 'Common configuration'

# 
# General
# 

GENERAL = (COMMON, 'General')

DEBUG_MODE                        = 'debug_mode'
SERVER_ADMIN                      = 'server_admin'
PROPAGATE_STACK_TRACES_TO_CLIENT  = 'propagate_stack_traces_to_client'
FACADE_TIMEOUT                    = 'facade_timeout'
SERVER_HOSTADDRESS                = 'server_hostaddress'

_sorted_variables.extend([
    (DEBUG_MODE,                       _Argument(GENERAL, bool,  False,      "If True, errors and exceptions are shown instead of generic feedback (like !WebLabInternalServerError)")),
    (SERVER_ADMIN,                     _Argument(GENERAL, str,   None,       "!WebLab-Deusto administrator's email address for notifications. See Admin Notifier settings below.")),
    (SERVER_HOSTADDRESS,               _Argument(GENERAL, str,   '',         "Host address of this WebLab-Deusto deployment")),
    (PROPAGATE_STACK_TRACES_TO_CLIENT, _Argument(GENERAL, bool,  False,      "If True, stacktraces are propagated to the client (useful for debugging).")),
    (FACADE_TIMEOUT,                   _Argument(GENERAL, float, 0.5,        "Seconds that the facade will wait accepting a connection before checking again for shutdown requests.")),
])

# 
# Admin notifier
# 

ADMIN_NOTIFIER = (COMMON, 'Admin Notifier')

MAIL_NOTIFICATION_ENABLED = 'mail_notification_enabled'
MAIL_SERVER_HOST          = 'mail_server_host'
MAIL_SERVER_HELO          = 'mail_server_helo'
MAIL_SERVER_USE_TLS       = 'mail_server_use_tls'
MAIL_NOTIFICATION_SENDER  = 'mail_notification_sender'
MAIL_NOTIFICATION_SUBJECT = 'mail_notification_subject'

_sorted_variables.extend([
    (MAIL_NOTIFICATION_ENABLED, _Argument(ADMIN_NOTIFIER, bool, NO_DEFAULT, "Enables or Disables mail notifications")),
    (MAIL_SERVER_HOST,          _Argument(ADMIN_NOTIFIER, str,  NO_DEFAULT, "Host to use for sending mail")),
    (MAIL_SERVER_HELO,          _Argument(ADMIN_NOTIFIER, str,  NO_DEFAULT, "Address to be used on the mail's HELO")),
    (MAIL_SERVER_USE_TLS,       _Argument(ADMIN_NOTIFIER, str,  'no',       "Use TLS or not. Values: 'yes' or 'no'")),
    (MAIL_NOTIFICATION_SENDER,  _Argument(ADMIN_NOTIFIER, str,  NO_DEFAULT, "Address of the mail's sender")), 
    (MAIL_NOTIFICATION_SUBJECT, _Argument(ADMIN_NOTIFIER, str,  "[WebLab] CRITICAL ERROR!", "(Optional) Subject of the notification mail")),
])

# 
# Database 
#

DATABASE = (COMMON, 'Database')

DB_HOST                         = 'db_host'
DB_DATABASE                     = 'db_database'
DB_ENGINE                       = 'db_engine'
WEBLAB_DB_USERNAME              = 'weblab_db_username'
WEBLAB_DB_PASSWORD              = 'weblab_db_password'
WEBLAB_DB_FORCE_ENGINE_CREATION = 'weblab_db_force_engine_creation'

_sorted_variables.extend([
    (DB_HOST,                         _Argument(DATABASE, str,  'localhost', "Location of the database server")),
    (DB_DATABASE,                     _Argument(DATABASE, str,  'WebLab',    "Name of the main database")),
    (DB_ENGINE,                       _Argument(DATABASE, str,  'mysql',     "Engine used. Example: mysql, sqlite")),
    (WEBLAB_DB_USERNAME,              _Argument(DATABASE, str,  "weblab",    "WebLab database username")),
    (WEBLAB_DB_PASSWORD,              _Argument(DATABASE, str,  NO_DEFAULT,  "WebLab database user password")),
    (WEBLAB_DB_FORCE_ENGINE_CREATION, _Argument(DATABASE, bool, False,       "Force the creation of an engine each time")),
])

# 
# Sessions
# 

SESSIONS = (COMMON, 'Sessions')

# !WebLab-Deusto supports two types of Session Managers:
#  * "Memory", storing all the sessions in memory. Fastest.
#  * "MySQL", storing all the sessions in MySQL tables. Far slower, but it can be shared among two servers to provide fault tolerance.

SESSION_MANAGER_DEFAULT_TIMEOUT              = 'session_manager_default_timeout'
SESSION_MEMORY_GATEWAY_SERIALIZE             = 'session_memory_gateway_serialize'

SESSION_SQLALCHEMY_ENGINE                    = 'session_sqlalchemy_engine'
SESSION_SQLALCHEMY_HOST                      = 'session_sqlalchemy_host'
SESSION_SQLALCHEMY_DB_NAME                   = 'session_sqlalchemy_db_name'
SESSION_SQLALCHEMY_USERNAME                  = 'session_sqlalchemy_username'
SESSION_SQLALCHEMY_PASSWORD                  = 'session_sqlalchemy_password'

SESSION_LOCK_SQLALCHEMY_ENGINE               = 'session_lock_sqlalchemy_engine'
SESSION_LOCK_SQLALCHEMY_HOST                 = 'session_lock_sqlalchemy_host'
SESSION_LOCK_SQLALCHEMY_DB_NAME              = 'session_lock_sqlalchemy_db_name'
SESSION_LOCK_SQLALCHEMY_USERNAME             = 'session_lock_sqlalchemy_username'
SESSION_LOCK_SQLALCHEMY_PASSWORD             = 'session_lock_sqlalchemy_password'

_sorted_variables.extend([
    (SESSION_SQLALCHEMY_ENGINE,                    _Argument(SESSIONS, str,  'mysql',           "Database engine used for sessions the database. Example: mysql")),
    (SESSION_SQLALCHEMY_HOST,                      _Argument(SESSIONS, str,  'localhost',       "Location of the sessions database server")),
    (SESSION_SQLALCHEMY_DB_NAME,                   _Argument(SESSIONS, str,  'WebLabSessions',  "Database name of the sessions database")),
    (SESSION_SQLALCHEMY_USERNAME,                  _Argument(SESSIONS, str,  NO_DEFAULT,        "Username for connecting to the sessions database" )),
    (SESSION_SQLALCHEMY_PASSWORD,                  _Argument(SESSIONS, str,  NO_DEFAULT,        "Password for connecting to the sessions database")),

    (SESSION_LOCK_SQLALCHEMY_ENGINE,               _Argument(SESSIONS, str,  'mysql',           "Database engine used for locking the database. Example: mysql")),
    (SESSION_LOCK_SQLALCHEMY_HOST,                 _Argument(SESSIONS, str,  'localhost',       "Location of the locking database server")),
    (SESSION_LOCK_SQLALCHEMY_DB_NAME,              _Argument(SESSIONS, str,  'WebLabSessions',  "Database name of the locking database")),
    (SESSION_LOCK_SQLALCHEMY_USERNAME,             _Argument(SESSIONS, str,  NO_DEFAULT,        "Username for connecting to the locking database" )),
    (SESSION_LOCK_SQLALCHEMY_PASSWORD,             _Argument(SESSIONS, str,  NO_DEFAULT,        "Password for connecting to the locking database")),

    (SESSION_MANAGER_DEFAULT_TIMEOUT,              _Argument(SESSIONS, int,  3600 * 2,          "Maximum time that a session will be stored in a Session Manager. In seconds.")),
    (SESSION_MEMORY_GATEWAY_SERIALIZE,             _Argument(SESSIONS, bool, False,             "Sessions can be stored in a database or in memory. If they are stored in memory, they can be serialized in memory or not, to check the behaviour")),
])


######################################
# 
# CORE SERVER
#

CORE_SERVER = 'Core Server'


# 
# General
# 

CORE = (CORE_SERVER,'General')

# || core_checking_time || int || 3 || How often the server will check what sessions have expired and delete them. Expressed in seconds. || 

WEBLAB_CORE_SERVER_SESSION_TYPE     = 'core_session_type'
WEBLAB_CORE_SERVER_SESSION_POOL_ID  = 'core_session_pool_id'

_sorted_variables.extend([
    (WEBLAB_CORE_SERVER_SESSION_TYPE,    _Argument(CORE, str, 'Memory', """What type of session manager the Core Server will use: Memory or MySQL.""")),
    (WEBLAB_CORE_SERVER_SESSION_POOL_ID, _Argument(CORE, str, 'UserProcessingServer', """ A unique identifier of the type of sessions, in order to manage them. For instance, if there are four servers (A, B, C and D), the load of users can be splitted in two groups: those being sent to A and B, and those being sent to C and D. A and B can share those sessions to provide fault tolerance (if A falls down, B can keep working from the same point A was) using a MySQL session manager, and the same may apply to C and D. The problem is that if A and B want to delete all the sessions -at the beginning, for example-, but they don't want to delete sessions of C and D, then they need a unique identifier shared for A and B, and another for C and D. In this case, "!UserProcessing_A_B" and "!UserProcessing_C_D" would be enough.""")),
])

# ==== Facade ====
# || *Property* || *Type* || *Default value* || *Description* || 
# || core_facade_server_route || str || "`<route-to-server>`" || Identifier of the server or groups of servers that will receive requests, for load balancing purposes. || 
# || core_facade_soap_bind || str || "" || Binding address for the SOAP facade at Core Server || 
# || core_facade_soap_port || int ||  || Port number for the SOAP facade at Core Server || 
# || core_facade_soap_service_name || str || "/!WebLab/soap/" || Service name for the SOAP facade at Core Server || 
# || core_facade_soap_public_server_host || str || "www.weblab.deusto.es" || Public server host, used for generating the WSDL file. || 
# || core_facade_soap_public_server_port || int || 80 || Public server port, used for generating the WSDL file. || 
# || core_facade_json_bind || str || "" || Binding address for the JSON facade at Core Server || 
# || core_facade_json_port || int ||  || Port number for the JSON facade at Core Server || 
# || core_facade_xmlrpc_bind || str || "" || Binding address for the XML-RPC facade at Core Server || 
# || core_facade_xmlrpc_port || int ||  || Port number for the XML-RPC facade at Core Server || 


#####################################
# 
# Generation
# 


variables = dict(_sorted_variables)

if __name__ == '__main__':
    categories = set([ variable.category for variable in variables.values() ])
    variables_by_category = {}

    sections = {}

    for category in categories:
        section, subsection = category
        subsections = sections.get(section, set())
        subsections.add(subsection)
        sections[section] = subsections
        variables_by_category[category] = [ variable for variable in variables if variables[variable].category == category ]

    for section in sections:
        print ' '.join(('=' * 3,section,'=' * 3))
        print
        for subsection in sections[section]:
            print ' '.join(('=' * 4,subsection,'=' * 4))
            print
            category = (section, subsection)
            print "|| *Property* || *Type* || *Default value* || *Description* ||"
            for variable, argument in _sorted_variables:
                if variable in variables_by_category[category]:
                    print "|| %(variable)s || %(type)s || %(default)s || %(doc)s ||" % {
                                        'variable' : variable,
                                        'type'     : variables[variable].type.__name__,
                                        'default'  : variables[variable].default if variables[variable].default is not NO_DEFAULT else '',
                                        'doc'      : variables[variable].message
                                    }
            print

