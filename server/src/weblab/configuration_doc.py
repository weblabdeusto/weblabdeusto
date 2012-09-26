from collections import namedtuple

NO_DEFAULT = object()
ANY_TYPE   = object()

_Argument = namedtuple('Argument', 'category type default message')

_sorted_variables = []


# 
# Regexp magic :-)
# :'<,'>s/|| \([a-z_]*\) || \([a-z]*\) || \(.*\) || \(.*\) ||/    (\U\1\E,      _Argument(COORDINATOR, \2, \3, """\4""")),/
# 

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
DB_PORT                         = 'db_port'
DB_DATABASE                     = 'db_database'
DB_ENGINE                       = 'db_engine'
WEBLAB_DB_USERNAME              = 'weblab_db_username'
WEBLAB_DB_PASSWORD              = 'weblab_db_password'
WEBLAB_DB_FORCE_ENGINE_CREATION = 'weblab_db_force_engine_creation'

_sorted_variables.extend([
    (DB_HOST,                         _Argument(DATABASE, str,  'localhost', "Location of the database server")),
    (DB_PORT,                         _Argument(DATABASE, int,  None,        "Port where the database is listening, if any")),
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
SESSION_SQLALCHEMY_PORT                      = 'session_sqlalchemy_port'
SESSION_SQLALCHEMY_DB_NAME                   = 'session_sqlalchemy_db_name'
SESSION_SQLALCHEMY_USERNAME                  = 'session_sqlalchemy_username'
SESSION_SQLALCHEMY_PASSWORD                  = 'session_sqlalchemy_password'

SESSION_LOCK_SQLALCHEMY_ENGINE               = 'session_lock_sqlalchemy_engine'
SESSION_LOCK_SQLALCHEMY_HOST                 = 'session_lock_sqlalchemy_host'
SESSION_LOCK_SQLALCHEMY_PORT                 = 'session_lock_sqlalchemy_port'
SESSION_LOCK_SQLALCHEMY_DB_NAME              = 'session_lock_sqlalchemy_db_name'
SESSION_LOCK_SQLALCHEMY_USERNAME             = 'session_lock_sqlalchemy_username'
SESSION_LOCK_SQLALCHEMY_PASSWORD             = 'session_lock_sqlalchemy_password'

_sorted_variables.extend([
    (SESSION_SQLALCHEMY_ENGINE,                    _Argument(SESSIONS, str,  'mysql',           "Database engine used for sessions the database. Example: mysql")),
    (SESSION_SQLALCHEMY_HOST,                      _Argument(SESSIONS, str,  'localhost',       "Location of the sessions database server")),
    (SESSION_SQLALCHEMY_PORT,                      _Argument(SESSIONS, int,  None,              "Location of the sessions database server")),
    (SESSION_SQLALCHEMY_DB_NAME,                   _Argument(SESSIONS, str,  'WebLabSessions',  "Database name of the sessions database")),
    (SESSION_SQLALCHEMY_USERNAME,                  _Argument(SESSIONS, str,  NO_DEFAULT,        "Username for connecting to the sessions database" )),
    (SESSION_SQLALCHEMY_PASSWORD,                  _Argument(SESSIONS, str,  NO_DEFAULT,        "Password for connecting to the sessions database")),

    (SESSION_LOCK_SQLALCHEMY_ENGINE,               _Argument(SESSIONS, str,  'mysql',           "Database engine used for locking the database. Example: mysql")),
    (SESSION_LOCK_SQLALCHEMY_HOST,                 _Argument(SESSIONS, str,  'localhost',       "Location of the locking database server")),
    (SESSION_LOCK_SQLALCHEMY_PORT,                 _Argument(SESSIONS, int,  None,              "Location of the locking database server")),
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
CORE_SERVER_URL                     = 'core_server_url'

_sorted_variables.extend([
    (WEBLAB_CORE_SERVER_SESSION_TYPE,    _Argument(CORE, str, 'Memory', """What type of session manager the Core Server will use: Memory or MySQL.""")),
    (WEBLAB_CORE_SERVER_SESSION_POOL_ID, _Argument(CORE, str, 'UserProcessingServer', """ A unique identifier of the type of sessions, in order to manage them. For instance, if there are four servers (A, B, C and D), the load of users can be splitted in two groups: those being sent to A and B, and those being sent to C and D. A and B can share those sessions to provide fault tolerance (if A falls down, B can keep working from the same point A was) using a MySQL session manager, and the same may apply to C and D. The problem is that if A and B want to delete all the sessions -at the beginning, for example-, but they don't want to delete sessions of C and D, then they need a unique identifier shared for A and B, and another for C and D. In this case, "!UserProcessing_A_B" and "!UserProcessing_C_D" would be enough.""")),
    (CORE_SERVER_URL,                    _Argument(CORE, str, NO_DEFAULT, "The base URL for this server. For instance, http://www.weblab.deusto.es/weblab/ ")),
])

# 
# Core Facade
# 

CORE_FACADE = (CORE_SERVER, 'Facade')

CORE_FACADE_SERVER_ROUTE            = 'core_facade_server_route'
CORE_FACADE_SOAP_BIND               = 'core_facade_soap_bind'
CORE_FACADE_SOAP_PORT               = 'core_facade_soap_port'
CORE_FACADE_SOAP_SERVICE_NAME       = 'core_facade_soap_service_name'
CORE_FACADE_SOAP_PUBLIC_SERVER_HOST = 'core_facade_soap_public_server_host'
CORE_FACADE_SOAP_PUBLIC_SERVER_PORT = 'core_facade_soap_public_server_port'
CORE_FACADE_JSON_BIND               = 'core_facade_json_bind'
CORE_FACADE_JSON_PORT               = 'core_facade_json_port'
CORE_FACADE_XMLRPC_BIND             = 'core_facade_xmlrpc_bind'
CORE_FACADE_XMLRPC_PORT             = 'core_facade_xmlrpc_port'

_sorted_variables.extend([
    (CORE_FACADE_SERVER_ROUTE,            _Argument(CORE_FACADE, str, 'default-route-to-server', """Identifier of the server or groups of servers that will receive requests, for load balancing purposes.""")),
    (CORE_FACADE_SOAP_BIND,               _Argument(CORE_FACADE, str, '',                        """Binding address for the SOAP facade at Core Server""")),
    (CORE_FACADE_SOAP_PORT,               _Argument(CORE_FACADE, int, NO_DEFAULT,                """Port number for the SOAP facade at Core Server""")),
    (CORE_FACADE_SOAP_SERVICE_NAME,       _Argument(CORE_FACADE, str, '/weblab/soap/',           """Service name for the SOAP facade at Core Server""")),
    (CORE_FACADE_SOAP_PUBLIC_SERVER_HOST, _Argument(CORE_FACADE, str, 'www.weblab.deusto.es',    """Public server host, used for generating the WSDL file.""")),
    (CORE_FACADE_SOAP_PUBLIC_SERVER_PORT, _Argument(CORE_FACADE, int, 80,                        """Public server port, used for generating the WSDL file.""")),
    (CORE_FACADE_JSON_BIND,               _Argument(CORE_FACADE, str, '',                        """Binding address for the JSON facade at Core Server""")),
    (CORE_FACADE_JSON_PORT,               _Argument(CORE_FACADE, int, NO_DEFAULT,                """Binding address for the JSON facade at Core Server""")),
    (CORE_FACADE_XMLRPC_BIND,             _Argument(CORE_FACADE, str, '',                        """Binding address for the XML-RPC facade at Core Server""")),
    (CORE_FACADE_XMLRPC_PORT,             _Argument(CORE_FACADE, int, NO_DEFAULT,                """Port number for the XML-RPC facade at Core Server""")),
])

# 
# Coordinator
# 

COORDINATOR = (CORE_SERVER, 'Coordinator')

COORDINATOR_DB_HOST            = 'core_coordinator_db_host'
COORDINATOR_DB_PORT            = 'core_coordinator_db_port'
COORDINATOR_DB_NAME            = 'core_coordinator_db_name'
COORDINATOR_DB_USERNAME        = 'core_coordinator_db_username'
COORDINATOR_DB_PASSWORD        = 'core_coordinator_db_password'
COORDINATOR_DB_ENGINE          = 'core_coordinator_db_engine'
COORDINATOR_LABORATORY_SERVERS = 'core_coordinator_laboratory_servers'
COORDINATOR_CLEAN              = 'core_coordinator_clean'

_sorted_variables.extend([
    (COORDINATOR_DB_HOST,            _Argument(COORDINATOR, str, "localhost", """Host of the database server.""")), 
    (COORDINATOR_DB_PORT,            _Argument(COORDINATOR, int, None,        """Port of the database server.""")), 
    (COORDINATOR_DB_NAME,            _Argument(COORDINATOR, str, "WebLabCoordination", """Name of the coordination database.""")), 
    (COORDINATOR_DB_USERNAME,        _Argument(COORDINATOR, str, NO_DEFAULT, """Username to access the coordination database.""")), 
    (COORDINATOR_DB_PASSWORD,        _Argument(COORDINATOR, str, NO_DEFAULT, """Password to access the coordination database.""")), 
    (COORDINATOR_DB_ENGINE,          _Argument(COORDINATOR, str, "mysql", """Driver used for the coordination database. We currently have only tested MySQL, although it should be possible to use other engines.""")), 
    (COORDINATOR_LABORATORY_SERVERS, _Argument(COORDINATOR, list, NO_DEFAULT, """Available laboratory servers. It's a list of strings, having each string this format: "laboratory1:main_instance@main_machine;exp1|ud-fpga|FPGA experiments", for the "laboratory1" in the instance "main_instance" at the machine "main_machine", which will handle the experiment instance "exp1" of the experiment type "ud-fpga" of the category "FPGA experiments". A laboratory can handle many experiments, and each experiment type may have many experiment instances with unique identifiers (such as "exp1" of "ud-fpga|FPGA experiments").""")), 
    (COORDINATOR_CLEAN,              _Argument(COORDINATOR, bool, True, """Whether this server will clean the coordinator tables or not. If there are two core servers, and one of them is turned off, you don't want that it deletes everything on the database when that server is turned on, because all the sessions handled by the other core server will be lost.""")), 
])


######################################
# 
# LOGIN SERVER
#

LOGIN_SERVER = 'Login Server'


# 
# Facade
# 

LOGIN_FACADE = (LOGIN_SERVER, 'Facade')

LOGIN_FACADE_TRUSTED_ADDRESSES       = 'login_facade_trusted_addresses'
LOGIN_FACADE_SOAP_BIND               = 'login_facade_soap_bind'
LOGIN_FACADE_SOAP_PORT               = 'login_facade_soap_port'
LOGIN_FACADE_SOAP_SERVICE_NAME       = 'login_facade_soap_service_name'
LOGIN_FACADE_SOAP_PUBLIC_SERVER_HOST = 'login_facade_soap_public_server_host'
LOGIN_FACADE_SOAP_PUBLIC_SERVER_PORT = 'login_facade_soap_public_server_port'
LOGIN_FACADE_JSON_BIND               = 'login_facade_json_bind'
LOGIN_FACADE_JSON_PORT               = 'login_facade_json_port'
LOGIN_FACADE_XMLRPC_BIND             = 'login_facade_xmlrpc_bind'
LOGIN_FACADE_XMLRPC_PORT             = 'login_facade_xmlrpc_port'

_sorted_variables.extend([
    (LOGIN_FACADE_TRUSTED_ADDRESSES,       _Argument(LOGIN_FACADE, tuple, ('127.0.0.1',), """The IP addresses on which the Login server will trust. Moodle can access !WebLab from a well known IP address, and if Moodle says "I'm user foo", and in !WebLab-Deusto, the user "foo" can be accessed from the IP address of that moodle, then Moodle will be able to log in as this user without any password.""")), 
    (LOGIN_FACADE_SOAP_BIND,               _Argument(LOGIN_FACADE, str, "", """Binding address for the SOAP facade at Login Server""")), 
    (LOGIN_FACADE_SOAP_PORT,               _Argument(LOGIN_FACADE, int, NO_DEFAULT, """Port number for the SOAP facade at Login Server""")), 
    (LOGIN_FACADE_SOAP_SERVICE_NAME,       _Argument(LOGIN_FACADE, str, "/weblab/login/soap/", """Service name for the SOAP facade at Login Server""")), 
    (LOGIN_FACADE_SOAP_PUBLIC_SERVER_HOST, _Argument(LOGIN_FACADE, str, "www.weblab.deusto.es", """Public server host, used for generating the WSDL file.""")), 
    (LOGIN_FACADE_SOAP_PUBLIC_SERVER_PORT, _Argument(LOGIN_FACADE, int, 80, """Public server port, used for generating the WSDL file.""")), 
    (LOGIN_FACADE_JSON_BIND,               _Argument(LOGIN_FACADE, str, "", """Binding address for the JSON facade at Login Server""")), 
    (LOGIN_FACADE_JSON_PORT,               _Argument(LOGIN_FACADE, int, NO_DEFAULT, """Port number for the JSON facade at Login Server""")), 
    (LOGIN_FACADE_XMLRPC_BIND,             _Argument(LOGIN_FACADE, str, "", """Binding address for the XML-RPC facade at Login Server""")), 
    (LOGIN_FACADE_XMLRPC_PORT,             _Argument(LOGIN_FACADE, int, NO_DEFAULT, """Port number for the XML-RPC facade at Login Server""")), 
])



######################################
# 
# LABORATORY SERVER
#

LABORATORY_SERVER = 'Laboratory Server'
LABORATORY = (LABORATORY_SERVER, 'General')

LABORATORY_SESSION_TYPE              = 'laboratory_session_type'
LABORATORY_SESSION_POOL_ID           = 'laboratory_session_pool_id'
LABORATORY_ASSIGNED_EXPERIMENTS      = 'laboratory_assigned_experiments'
LABORATORY_EXCLUDE_CHECKING          = 'laboratory_exclude_checking'

_sorted_variables.extend([
    (LABORATORY_SESSION_TYPE,         _Argument(LABORATORY, str, "Memory", """What type of session manager the Core Server will use: Memory or MySQL.""")), 
    (LABORATORY_SESSION_POOL_ID,      _Argument(LABORATORY, str, "LaboratoryServer", """See "core_session_pool_id" in the core server.""")), 
    (LABORATORY_ASSIGNED_EXPERIMENTS, _Argument(LABORATORY, list, NO_DEFAULT, """List of strings representing which experiments are available through this particular laboratory server. Each string contains something like 'exp1|ud-fpga|FPGA experiments;experiment_fpga:main_instance@main_machine', where exp1|ud-fpga|FPGA experiments is the identifier of the experiment (see core_coordinator_laboratory_servers), and "experiment_fpga:main_instance@main_machine" is the !WebLab Address of the experiment server.""")), 
    (LABORATORY_EXCLUDE_CHECKING,     _Argument(LABORATORY, list, [], """List of ids of experiments upon which checks will not be run""")), 
])


######################################
# 
# PROXY SERVER
#

PROXY_SERVER = 'Proxy Server'
PROXY = (PROXY_SERVER, 'General')

PROXY_EXPERIMENT_POLL_TIME         = 'proxy_experiment_poll_time'
PROXY_STORE_STUDENTS_PROGRAMS_PATH = 'proxy_store_students_programs_path'

_sorted_variables.extend([
    (PROXY_EXPERIMENT_POLL_TIME,         _Argument(PROXY, int, 30, """Maximum amount of time that the server will wait for polls from a user using an experiment, in seconds, before considering that the user is not connected anymore.""")), 
    (PROXY_STORE_STUDENTS_PROGRAMS_PATH, _Argument(PROXY, str, NO_DEFAULT, """Local path to store the files sent by the students with send_file() (only when the proper Translator decides to store the program).""")), 
])



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

