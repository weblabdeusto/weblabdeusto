from __future__ import print_function, unicode_literals
from collections import namedtuple

NO_DEFAULT = object()
ANY_TYPE   = object()

_Argument = namedtuple('Argument', 'category type default message')

_sorted_variables = []

DESCRIPTIONS = {}

# 
# Regexp magic :-)
# :'<,'>s/|| \([a-z_]*\) || \([a-z]*\) || \(.*\) || \(.*\) ||/    (\U\1\E,      _Argument(COORDINATOR, \2, \3, """\4""")),/
# 

######################################
# 
# COMMON
# 

COMMON = 'Common configuration'
DESCRIPTIONS[COMMON] = """These variables affect all the servers. For instance, certain servers use a session manager (e.g. the Core server for users, but also the Laboratory server)."""

# 
# General
# 

GENERAL = (COMMON, 'General')
DESCRIPTIONS[GENERAL] = """These variables are simple variables which are general to the whole project."""

DEBUG_MODE                        = 'debug_mode'
SERVER_ADMIN                      = 'server_admin'
PROPAGATE_STACK_TRACES_TO_CLIENT  = 'propagate_stack_traces_to_client'
FACADE_TIMEOUT                    = 'facade_timeout'
SERVER_HOSTADDRESS                = 'server_hostaddress'

_sorted_variables.extend([
    (DEBUG_MODE,                       _Argument(GENERAL, bool,         False,      "If True, errors and exceptions are shown instead of generic feedback (like WebLabInternalServerError)")),
    (SERVER_ADMIN,                     _Argument(GENERAL, basestring,   None,       "WebLab-Deusto administrator's email address for notifications. See Admin Notifier settings below.")),
    (SERVER_HOSTADDRESS,               _Argument(GENERAL, basestring,   '',         "Host address of this WebLab-Deusto deployment")),
    (PROPAGATE_STACK_TRACES_TO_CLIENT, _Argument(GENERAL, bool,         False,      "If True, stacktraces are propagated to the client (useful for debugging).")),
    (FACADE_TIMEOUT,                   _Argument(GENERAL, float,        0.5,        "Seconds that the facade will wait accepting a connection before checking again for shutdown requests.")),
])

# 
# Admin notifier
# 

ADMIN_NOTIFIER = (COMMON, 'Admin Notifier')
DESCRIPTIONS[ADMIN_NOTIFIER] = """The Admin notifier is mainly used by the core server for notifying administrators of certain activity such as broken laboratories."""

MAIL_NOTIFICATION_ENABLED = 'mail_notification_enabled'
MAIL_SERVER_HOST          = 'mail_server_host'
MAIL_SERVER_HELO          = 'mail_server_helo'
MAIL_SERVER_USE_TLS       = 'mail_server_use_tls'
MAIL_NOTIFICATION_SENDER  = 'mail_notification_sender'
MAIL_NOTIFICATION_SUBJECT = 'mail_notification_subject'

_sorted_variables.extend([
    (MAIL_NOTIFICATION_ENABLED, _Argument(ADMIN_NOTIFIER, bool, NO_DEFAULT, "Enables or Disables mail notifications")),
    (MAIL_SERVER_HOST,          _Argument(ADMIN_NOTIFIER, basestring,  NO_DEFAULT, "Host to use for sending mail")),
    (MAIL_SERVER_HELO,          _Argument(ADMIN_NOTIFIER, basestring,  NO_DEFAULT, "Address to be used on the mail's HELO")),
    (MAIL_SERVER_USE_TLS,       _Argument(ADMIN_NOTIFIER, basestring,  'no',       "Use TLS or not. Values: 'yes' or 'no'")),
    (MAIL_NOTIFICATION_SENDER,  _Argument(ADMIN_NOTIFIER, basestring,  NO_DEFAULT, "Address of the mail's sender")), 
    (MAIL_NOTIFICATION_SUBJECT, _Argument(ADMIN_NOTIFIER, basestring,  "[WebLab] CRITICAL ERROR!", "(Optional) Subject of the notification mail")),
])

# 
# Database 
#

DATABASE = (COMMON, 'Database')
DESCRIPTIONS[DATABASE] = """The database configuration applies to the Core Server and the Login Server (which both connect to the same database)."""

DB_HOST                  = 'db_host'
DB_PORT                  = 'db_port'
DB_DATABASE              = 'db_database'
DB_ENGINE                = 'db_engine'
DB_ECHO                  = 'db_echo'
DB_POOL_SIZE             = 'db_pool_size'
DB_MAX_OVERFLOW          = 'db_max_overflow'
DB_USERNAME              = 'weblab_db_username'
DB_PASSWORD              = 'weblab_db_password'
DB_FORCE_ENGINE_CREATION = 'weblab_db_force_engine_creation'

_sorted_variables.extend([
    (DB_HOST,                         _Argument(DATABASE, basestring, 'localhost',  "Location of the database server")),
    (DB_PORT,                         _Argument(DATABASE, int,               None,  "Port where the database is listening, if any")),
    (DB_DATABASE,                     _Argument(DATABASE, basestring,    'WebLab',  "Name of the main database")),
    (DB_ENGINE,                       _Argument(DATABASE, basestring,     'mysql',  "Engine used. Example: mysql, sqlite")),
    (DB_ECHO,                         _Argument(DATABASE, bool,             False,  "Display in stdout all the SQL sentences")),
    (DB_POOL_SIZE,                    _Argument(DATABASE, int,                  5,  "Maximum number of spare connections to the database.")),
    (DB_MAX_OVERFLOW,                 _Argument(DATABASE, int,                 35,  "Maximum number of connections to the database.")),
    (DB_USERNAME,                     _Argument(DATABASE, basestring,    "weblab",  "WebLab database username")),
    (DB_PASSWORD,                     _Argument(DATABASE, basestring,  NO_DEFAULT,  "WebLab database user password")),
    (DB_FORCE_ENGINE_CREATION,        _Argument(DATABASE, bool,             False,  "Force the creation of an engine each time")),
])

# 
# Sessions
# 

SESSIONS = (COMMON, 'Sessions')
DESCRIPTIONS[SESSIONS] = """The session configuration is mainly used by the Core Server, but also by the Laboratory Server and by certain Experiment Servers."""

# WebLab-Deusto supports two types of Session Managers:
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
    (SESSION_SQLALCHEMY_ENGINE,                    _Argument(SESSIONS, basestring,  'mysql',           "Database engine used for sessions the database. Example: mysql")),
    (SESSION_SQLALCHEMY_HOST,                      _Argument(SESSIONS, basestring,  'localhost',       "Location of the sessions database server")),
    (SESSION_SQLALCHEMY_PORT,                      _Argument(SESSIONS, int,  None,              "Location of the sessions database server")),
    (SESSION_SQLALCHEMY_DB_NAME,                   _Argument(SESSIONS, basestring,  'WebLabSessions',  "Database name of the sessions database")),
    (SESSION_SQLALCHEMY_USERNAME,                  _Argument(SESSIONS, basestring,  NO_DEFAULT,        "Username for connecting to the sessions database" )),
    (SESSION_SQLALCHEMY_PASSWORD,                  _Argument(SESSIONS, basestring,  NO_DEFAULT,        "Password for connecting to the sessions database")),

    (SESSION_LOCK_SQLALCHEMY_ENGINE,               _Argument(SESSIONS, basestring,  'mysql',           "Database engine used for locking the database. Example: mysql")),
    (SESSION_LOCK_SQLALCHEMY_HOST,                 _Argument(SESSIONS, basestring,  'localhost',       "Location of the locking database server")),
    (SESSION_LOCK_SQLALCHEMY_PORT,                 _Argument(SESSIONS, int,  None,              "Location of the locking database server")),
    (SESSION_LOCK_SQLALCHEMY_DB_NAME,              _Argument(SESSIONS, basestring,  'WebLabSessions',  "Database name of the locking database")),
    (SESSION_LOCK_SQLALCHEMY_USERNAME,             _Argument(SESSIONS, basestring,  NO_DEFAULT,        "Username for connecting to the locking database" )),
    (SESSION_LOCK_SQLALCHEMY_PASSWORD,             _Argument(SESSIONS, basestring,  NO_DEFAULT,        "Password for connecting to the locking database")),

    (SESSION_MANAGER_DEFAULT_TIMEOUT,              _Argument(SESSIONS, int,  3600 * 2,          "Maximum time that a session will be stored in a Session Manager. In seconds.")),
    (SESSION_MEMORY_GATEWAY_SERIALIZE,             _Argument(SESSIONS, bool, False,             "Sessions can be stored in a database or in memory. If they are stored in memory, they can be serialized in memory or not, to check the behaviour")),
])


######################################
# 
# CORE SERVER
#

CORE_SERVER = 'Core Server'

DESCRIPTIONS[CORE_SERVER] = """This configuration is used only by the Core servers. The Core server manages the scheduling, life cycle of the users, the sessions, and the incoming web services calls. Note that there is other common configuration which affects the Core server, so also take a look at the Common Configuration in this document."""

# 
# General
# 

CORE = (CORE_SERVER,'General')
DESCRIPTIONS[CORE] = """General variables for the Core server: what type of session, should we store students programs, etc."""

# || core_checking_time || int || 3 || How often the server will check what sessions have expired and delete them. Expressed in seconds. || 

WEBLAB_CORE_SERVER_SESSION_TYPE     = 'core_session_type'
WEBLAB_CORE_SERVER_SESSION_POOL_ID  = 'core_session_pool_id'
CORE_SERVER_URL                     = 'core_server_url'
CORE_STORE_STUDENTS_PROGRAMS        = 'core_store_students_programs'
CORE_STORE_STUDENTS_PROGRAMS_PATH   = 'core_store_students_programs_path'
CORE_UNIVERSAL_IDENTIFIER           = 'core_universal_identifier'
CORE_UNIVERSAL_IDENTIFIER_HUMAN     = 'core_universal_identifier_human'
CORE_GEOIP2_CITY_FILEPATH           = 'geoip2_city_filepath'
CORE_GEOIP2_COUNTRY_FILEPATH        = 'geoip2_country_filepath'
CORE_LOCAL_CITY                     = 'local_city'
CORE_LOCAL_COUNTRY                  = 'local_country'
CORE_IGNORE_LOCATIONS               = 'ignore_locations'
CORE_LOGO_PATH                      = 'logo_path'
CORE_LOGO_SMALL_PATH                = 'logo_small_path'

_sorted_variables.extend([
    # URL, identifiers
    (CORE_SERVER_URL,                    _Argument(CORE, basestring, NO_DEFAULT, "The base URL for this server. For instance, http://your-uni.edu/weblab/ ")),
    (CORE_UNIVERSAL_IDENTIFIER,          _Argument(CORE, basestring, '00000000', """Unique global ID for this WebLab-Deusto deployment. Used in federated environments, where multiple nodes register each other and do not want to enter in a loop. You should generate one (search for online GUID or UUID generators or use the uuid module in Python).""")),
    (CORE_UNIVERSAL_IDENTIFIER_HUMAN,    _Argument(CORE, basestring, 'WARNING; MISCONFIGURED SERVER. ADD A UNIVERSAL IDENTIFIER', """Message such as 'University A', which identifies which system is using performing the reservation. The unique identifier above must be unique, but this one only helps debugging.""")),

    # Sessions
    (WEBLAB_CORE_SERVER_SESSION_TYPE,    _Argument(CORE, basestring, 'Memory', """What type of session manager the Core Server will use: Memory or MySQL.""")),
    (WEBLAB_CORE_SERVER_SESSION_POOL_ID, _Argument(CORE, basestring, 'UserProcessingServer', """ A unique identifier of the type of sessions, in order to manage them. For instance, if there are four servers (A, B, C and D), the load of users can be splitted in two groups: those being sent to A and B, and those being sent to C and D. A and B can share those sessions to provide fault tolerance (if A falls down, B can keep working from the same point A was) using a MySQL session manager, and the same may apply to C and D. The problem is that if A and B want to delete all the sessions -at the beginning, for example-, but they don't want to delete sessions of C and D, then they need a unique identifier shared for A and B, and another for C and D. In this case, "UserProcessing_A_B" and "UserProcessing_C_D" would be enough.""")),

    (CORE_STORE_STUDENTS_PROGRAMS,       _Argument(CORE, bool, False, "Whether files submitted by users should be stored or not. ")),
    (CORE_STORE_STUDENTS_PROGRAMS_PATH,  _Argument(CORE, basestring, None, "If files are stored, in which local directory should be stored.")),
    (CORE_GEOIP2_CITY_FILEPATH,          _Argument(CORE, basestring, "GeoLite2-City.mmdb", "If the maxminds city database is downloaded, use it")),
    (CORE_GEOIP2_COUNTRY_FILEPATH,       _Argument(CORE, basestring, "GeoLite2-Country.mmdb", "If the maxminds country database is downloaded, use it")),
    (CORE_LOCAL_CITY,                    _Argument(CORE, basestring, None, "Local city (e.g., if deployed in Bilbao, should be Bilbao). This is used so WebLab-Deusto uses it for resolving local IP addresses")),
    (CORE_LOCAL_COUNTRY,                 _Argument(CORE, basestring, None, "Local country, in ISO 3166 format (e.g., if deployed in Spain, should be ES). This is used so WebLab-Deusto uses it for resolving local IP addresses")),
    (CORE_IGNORE_LOCATIONS,              _Argument(CORE, bool, False, "Ignore the locations system (and therefore do not print any error if the files are not found)")),
    (CORE_LOGO_PATH,                     _Argument(CORE, basestring, 'client/images/logo.jpg', "File path of the logo.")),
    (CORE_LOGO_SMALL_PATH,               _Argument(CORE, basestring, 'client/images/logo-mobile.jpg', "File path of the small version of the logo.")),
])

# 
# Core Facade
# 

CORE_FACADE = (CORE_SERVER, 'Facade')
DESCRIPTIONS[CORE_FACADE] = """Here you can customize the general web services consumed by the clients. Stuff like which ports will be used, etc."""

CORE_FACADE_SERVER_ROUTE            = 'core_facade_server_route'

CORE_FACADE_BIND                    = 'core_facade_bind'
CORE_FACADE_PORT                    = 'core_facade_port'

_sorted_variables.extend([
    (CORE_FACADE_SERVER_ROUTE,            _Argument(CORE_FACADE, basestring, 'default-route-to-server', """Identifier of the server or groups of servers that will receive requests, for load balancing purposes.""")),
    (CORE_FACADE_BIND,                    _Argument(CORE_FACADE, basestring, '',                 """Binding address for the main facade at Core server""")), 
    (CORE_FACADE_PORT,                    _Argument(CORE_FACADE, int, NO_DEFAULT,                """Binding address for the main facade at Core Server""")),
])

# 
# Coordinator
# 

COORDINATOR = (CORE_SERVER, 'Scheduling')
DESCRIPTIONS[COORDINATOR] = """This is the configuration variables used by the scheduling backend (called Coordinator). Basically, you can choose among redis or a SQL based one, and customize the one selected."""

COORDINATOR_IMPL               = 'core_coordination_impl'
COORDINATOR_DB_HOST            = 'core_coordinator_db_host'
COORDINATOR_DB_PORT            = 'core_coordinator_db_port'
COORDINATOR_DB_NAME            = 'core_coordinator_db_name'
COORDINATOR_DB_USERNAME        = 'core_coordinator_db_username'
COORDINATOR_DB_PASSWORD        = 'core_coordinator_db_password'
COORDINATOR_DB_ENGINE          = 'core_coordinator_db_engine'
COORDINATOR_LABORATORY_SERVERS = 'core_coordinator_laboratory_servers'

_sorted_variables.extend([
    (COORDINATOR_IMPL,               _Argument(COORDINATOR, basestring, "sqlalchemy", "Which scheduling backend will be used. Current implementations: 'redis', 'sqlalchemy'.")),
    (COORDINATOR_DB_HOST,            _Argument(COORDINATOR, basestring, "localhost", """Host of the database server.""")), 
    (COORDINATOR_DB_PORT,            _Argument(COORDINATOR, int, None,        """Port of the database server.""")), 
    (COORDINATOR_DB_NAME,            _Argument(COORDINATOR, basestring, "WebLabCoordination", """Name of the coordination database.""")), 
    (COORDINATOR_DB_USERNAME,        _Argument(COORDINATOR, basestring, NO_DEFAULT, """Username to access the coordination database.""")), 
    (COORDINATOR_DB_PASSWORD,        _Argument(COORDINATOR, basestring, NO_DEFAULT, """Password to access the coordination database.""")), 
    (COORDINATOR_DB_ENGINE,          _Argument(COORDINATOR, basestring, "mysql", """Driver used for the coordination database. We currently have only tested MySQL, although it should be possible to use other engines.""")), 
    (COORDINATOR_LABORATORY_SERVERS, _Argument(COORDINATOR, list, NO_DEFAULT, """Available laboratory servers. It's a list of strings, having each string this format: "lab1:inst@mach;exp1|ud-fpga|FPGA experiments", for the "lab1" in the instance "inst" at the machine "mach", which will handle the experiment instance "exp1" of the experiment type "ud-fpga" of the category "FPGA experiments". A laboratory can handle many experiments, and each experiment type may have many experiment instances with unique identifiers (such as "exp1" of "ud-fpga|FPGA experiments").""")), 
])


######################################
# 
# LOGIN SERVER
#

LOGIN_SERVER = 'Login Server'

DESCRIPTIONS[LOGIN_SERVER] = """This configuration is used only by the Login servers. The Login server manages the authentication requests and check the credentials (e.g. LDAP, OpenID, OAuth 2.0 or using the database). It is the only server which ever transports a password. Note that there is other common configuration which affects the Login server, so also take a look at the Common Configuration in this document."""

# 
# Facade
# 

LOGIN_FACADE = (LOGIN_SERVER, 'Facade')
DESCRIPTIONS[LOGIN_FACADE] = """The login facade configuration variables are used by the web services interface. You can change the ports, etc., but take into account the final web server (e.g. Apache) configuration."""

LOGIN_FACADE_TRUSTED_ADDRESSES       = 'login_facade_trusted_addresses'
LOGIN_FACADE_SERVER_ROUTE            = 'login_facade_server_route'

_sorted_variables.extend([
    (LOGIN_FACADE_TRUSTED_ADDRESSES,       _Argument(LOGIN_FACADE, tuple, ('127.0.0.1',), """The IP addresses on which the Login server will trust. Moodle can access WebLab from a well known IP address, and if Moodle says "I'm user foo", and in WebLab-Deusto, the user "foo" can be accessed from the IP address of that moodle, then Moodle will be able to log in as this user without any password.""")), 
    (LOGIN_FACADE_SERVER_ROUTE,            _Argument(LOGIN_FACADE, basestring, 'default-route-to-server', """Identifier of the server or groups of servers that will receive requests, for load balancing purposes.""")),
])



######################################
# 
# LABORATORY SERVER
#

LABORATORY_SERVER = 'Laboratory Server'
DESCRIPTIONS[LABORATORY_SERVER] = """The laboratory server is closer to the experiment server and checks if it is alive, maintains the sessions and acts as a bridge between the pool of core servers and the experiments."""
LABORATORY = (LABORATORY_SERVER, 'General')

LABORATORY_SESSION_TYPE              = 'laboratory_session_type'
LABORATORY_SESSION_POOL_ID           = 'laboratory_session_pool_id'
LABORATORY_ASSIGNED_EXPERIMENTS      = 'laboratory_assigned_experiments'
LABORATORY_EXCLUDE_CHECKING          = 'laboratory_exclude_checking'

_sorted_variables.extend([
    (LABORATORY_SESSION_TYPE,         _Argument(LABORATORY, basestring, "Memory", """What type of session manager the Core Server will use: Memory or MySQL.""")), 
    (LABORATORY_SESSION_POOL_ID,      _Argument(LABORATORY, basestring, "LaboratoryServer", """See "core_session_pool_id" in the core server.""")), 
    (LABORATORY_ASSIGNED_EXPERIMENTS, _Argument(LABORATORY, list, NO_DEFAULT, """List of strings representing which experiments are available through this particular laboratory server. Each string contains something like 'exp1|ud-fpga|FPGA experiments;fpga:inst@mach', where exp1|ud-fpga|FPGA experiments is the identifier of the experiment, and "fpga:inst@mach" is the WebLab Address of the experiment server.""")), 
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
    (PROXY_STORE_STUDENTS_PROGRAMS_PATH, _Argument(PROXY, basestring, NO_DEFAULT, """Local path to store the files sent by the students with send_file() (only when the proper Translator decides to store the program).""")), 
])


#####################################
# 
# EXPERIMENTS
# 

EXPERIMENTS = 'Experiments'
DESCRIPTIONS[EXPERIMENTS] = "This section includes the configuration of existing laboratories."

HTTP_EXPERIMENT = (EXPERIMENTS, 'HTTP')
DESCRIPTIONS[HTTP_EXPERIMENT] = "The HTTP experiment is a type of unmanaged laboratory which enables you to develop your own laboratory. WebLab-Deusto will call certain methods in that laboratory, and your laboratory will act taking that into account."

HTTP_EXPERIMENT_URL      = 'http_experiment_url'
HTTP_EXPERIMENT_USERNAME = 'http_experiment_username'
HTTP_EXPERIMENT_PASSWORD = 'http_experiment_password'
HTTP_EXPERIMENT_BATCH    = 'http_experiment_batch'


_sorted_variables.extend([
    (HTTP_EXPERIMENT_URL,          _Argument(HTTP_EXPERIMENT, basestring, NO_DEFAULT, "The base URL for the experiment server. Example: 'http://address/mylab/' will perform requests to 'http://address/mylab/weblab/")),
    (HTTP_EXPERIMENT_USERNAME,     _Argument(HTTP_EXPERIMENT, basestring, None, "The username used for performing that request. If not present, it will not use any credentials (and it will assume that the server is filtering the address by IP address or so).")),
    (HTTP_EXPERIMENT_PASSWORD,     _Argument(HTTP_EXPERIMENT, basestring, None, "The password used for performing that request. If not present, it will not use any credentials.")),
    (HTTP_EXPERIMENT_BATCH,        _Argument(HTTP_EXPERIMENT, bool, False, "Does the system manage its own scheduling mechanism? If so, users requesting access will automatically be forwarded, and it is the experiment server the one who has to manage what to do with them.")),
])



#####################################
# 
# Generation
# 


variables = dict(_sorted_variables)

if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-f", "--format", dest="format", default='sphinx', choices=('gcode','sphinx'),
                      help="use FORMAT (gcode, sphinx)", metavar="FORMAT")
    (options, args) = parser.parse_args()

    categories = set([ variable.category for variable in variables.values() ])
    # Ignore proxy
    categories.remove(PROXY)

    variables_by_category = {}

    sections = {}

    for category in categories:
        section, subsection = category
        subsections = sections.get(section, [])
        if subsection == 'General':
            subsections.insert(0, subsection)
        else:
            subsections.append(subsection)
        sections[section] = subsections
        variables_by_category[category] = [ variable for variable in variables if variables[variable].category == category ]

    if options.format == 'gcode':
        for section in sections:
            print(' '.join(('=' * 3,section,'=' * 3)))
            print()
            for subsection in sections[section]:
                print(' '.join(('=' * 4,subsection,'=' * 4)))
                print()
                category = (section, subsection)
                print("|| *Property* || *Type* || *Default value* || *Description* ||")
                for variable, argument in _sorted_variables:
                    if variable in variables_by_category[category]:
                        print("|| %(variable)s || %(type)s || %(default)s || %(doc)s ||" % {
                                            'variable' : variable,
                                            'type'     : variables[variable].type.__name__,
                                            'default'  : variables[variable].default if variables[variable].default is not NO_DEFAULT else '',
                                            'doc'      : variables[variable].message
                                        })
                print()
    elif options.format == 'sphinx':
        print(".. DO NOT EDIT THIS FILE. It has been autogenerated at weblab/server/src/weblab/configuration_doc.py")
        print()
        print(".. _configuration_variables:")
        print()
        print("Configuration variables")
        print("=======================")
        print()
        print("This section covers the available configuration variables, organized by")
        print("servers. Take a look at :ref:`technical_description` to identify the ")
        print("different servers described here.")
        print()
        print(".. note::")
        print()
        print("   At the time of this writing, not all the variables have been documented. We're working on this (March 2013).")
        print()
        print(".. contents:: Table of Contents")
        print()
        for section in sections:
            print(section)
            print('-' * len(section))
            print()
            if section in DESCRIPTIONS:
                print(DESCRIPTIONS[section])
                print()

            for subsection in sections[section]:
                
                print(subsection)
                print('^' * len(subsection))
                print()

                category = (section, subsection)

                if category in DESCRIPTIONS:
                    print(DESCRIPTIONS[category])
                    print()

                header1 = '*Property*'
                header2 = '*Type*'
                header3 = '*Default value*'
                header4 = '*Description*'

                max_c1, max_c2, max_c3, max_c4 = len(header1), len(header2), len(header3), len(header4)

                for variable, argument in _sorted_variables:
                    if variable in variables_by_category[category]:
                        name    = variable
                        type    = variables[variable].type.__name__
                        default = unicode(variables[variable].default if variables[variable].default is not NO_DEFAULT else '')
                        doc     = variables[variable].message

                        if len(name) > max_c1:
                            max_c1 = len(name)
                        if len(type) > max_c2:
                            max_c2 = len(type)
                        if len(default) > max_c3:
                            max_c3 = len(default)
                        if len(doc) > max_c4:
                            max_c4 = len(doc)
                
                def sfill(s, n):
                    return s + ' ' * (n - len(s))

                def print_row(s1, s2, s3, s4):
                    print(sfill(s1, max_c1), sfill(s2, max_c2), sfill(s3, max_c3), sfill(s4, max_c4))
                    
                print('=' * max_c1,   '=' * max_c2,   '=' * max_c3,   '=' * max_c4)
                print_row(header1, header2, header3, header4)
                print('=' * max_c1,   '=' * max_c2,   '=' * max_c3,   '=' * max_c4)
                for variable, argument in _sorted_variables:
                    if variable in variables_by_category[category]:
                        name    = variable
                        type    = variables[variable].type.__name__
                        default = unicode(variables[variable].default if variables[variable].default is not NO_DEFAULT else '')
                        doc     = variables[variable].message
                        print_row(name, type, default, doc)

                print('=' * max_c1,   '=' * max_c2,   '=' * max_c3,   '=' * max_c4)


                print()

    else:
        print("Error: unknown format: %s" % options.format)

