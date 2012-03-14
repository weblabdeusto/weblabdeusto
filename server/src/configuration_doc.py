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

# Coordinator
# || *Property* || *Type* || *Default value* || *Description* || 
# || core_coordinator_db_host || str || "localhost" || Host of the database server. || 
# || core_coordinator_db_name || str || "!WebLabCoordination" || Name of the coordination database. || 
# || core_coordinator_db_username || str ||  || Username to access the coordination database. || 
# || core_coordinator_db_password || str ||  || Password to access the coordination database. || 
# || core_coordinator_db_engine || str || "mysql" || Driver used for the coordination database. We currently have only tested MySQL, although it should be possible to use other engines. || 
# || core_coordinator_laboratory_servers || list ||  || Available laboratory servers. It's a list of strings, having each string this format: "laboratory1:main_instance@main_machine;exp1|ud-fpga|FPGA experiments", for the "laboratory1" in the instance "main_instance" at the machine "main_machine", which will handle the experiment instance "exp1" of the experiment type "ud-fpga" of the category "FPGA experiments". A laboratory can handle many experiments, and each experiment type may have many experiment instances with unique identifiers (such as "exp1" of "ud-fpga|FPGA experiments"). || 
# || core_coordinator_clean || bool || True || Whether this server will clean the coordinator tables or not. If there are two core servers, and one of them is turned off, you don't want that it deletes everything on the database when that server is turned on, because all the sessions handled by the other core server will be lost. || 



# === Login Server ===
# 
# ==== Facade ====
# || *Property* || *Type* || *Default value* || *Description* || 
# || login_facade_trusted_addresses || tuple || ('127.0.0.1',) || The IP addresses on which the Login server will trust. Moodle can access !WebLab from a well known IP address, and if Moodle says "I'm user foo", and in !WebLab-Deusto, the user "foo" can be accessed from the IP address of that moodle, then Moodle will be able to log in as this user without any password. || 
# || login_facade_soap_bind || str || "" || Binding address for the SOAP facade at Login Server || 
# || login_facade_soap_port || int ||  || Port number for the SOAP facade at Login Server || 
# || login_facade_soap_service_name || str || "/!WebLab/login/soap/" || Service name for the SOAP facade at Login Server || 
# || login_facade_soap_public_server_host || str || "www.weblab.deusto.es" || Public server host, used for generating the WSDL file. || 
# || login_facade_soap_public_server_port || int || 80 || Public server port, used for generating the WSDL file. || 
# || login_facade_json_bind || str || "" || Binding address for the JSON facade at Login Server || 
# || login_facade_json_port || int ||  || Port number for the JSON facade at Login Server || 
# || login_facade_xmlrpc_bind || str || "" || Binding address for the XML-RPC facade at Login Server || 
# || login_facade_xmlrpc_port || int ||  || Port number for the XML-RPC facade at Login Server || 
# 
# 
# === Proxy Server ===
# || *Property* || *Type* || *Default value* || *Description* || 
# || proxy_experiment_poll_time || int || 30 || Maximum amount of time that the server will wait for polls from a user using an experiment, in seconds, before considering that the user is not connected anymore. || 
# || proxy_store_students_programs_path || str ||  || Local path to store the files sent by the students with send_file() (only when the proper Translator decides to store the program). || 
# 
# 
# === Laboratory Server ===
# || *Property* || *Type* || *Default value* || *Description* || 
# || laboratory_session_type || str || "Memory" || What type of session manager the Core Server will use: Memory or MySQL. || 
# || laboratory_session_pool_id || str || "!LaboratoryServer" || See "core_session_pool_id" in the core server. || 
# || laboratory_assigned_experiments || list ||  || List of strings representing which experiments are available through this particular laboratory server. Each string contains something like 'exp1|ud-fpga|FPGA experiments;experiment_fpga:main_instance@main_machine', where exp1|ud-fpga|FPGA experiments is the identifier of the experiment (see core_coordinator_laboratory_servers), and "experiment_fpga:main_instance@main_machine" is the !WebLab Address of the experiment server. || 
# || laboratory_exclude_checking || list || [] || List of ids of experiments upon which checks will not be run || 
# 
# === Experiment Server ===
# 
# Apart from the general properties, every Experiment Developer can add as many properties as desired in order to make the experiment parametrizable. For instance, the GPIB *experiment* developed at the University of Deusto has its own properties:
# 
# || *Property* || *Type* || *Default value* || *Description* || 
# || gpib_just_testing || bool || False || Only testing the server or not. || 
# || gpib_public_output_file_filename || str ||  || The expected file name that the server will check after the experiment was executed. || 
# 
# Since Experiment Developers can develop both experiments and reutilizable devices, both components can manage their own properties. Following the same example, the GPIB experiment makes use of a generic GPIB *device* cappable of managing the particularities of a generic GPIB connection. And this device has the following properties:
# 
# || *Property* || *Type* || *Default value* || *Description* || 
# || gpib_compiler_command || str ||  || A list as ['bcc32','-c','$CPP_FILE'], so as to compile with the Borland C Compiler || 
# || gpib_linker_command || str ||  || A list as ["ilink32","-Tpe","-c","$OBJ_FILE","c0x32,", "$EXE_FILE,",",","visa32","import32","cw32"] for linking the compiled object || 
# 

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

