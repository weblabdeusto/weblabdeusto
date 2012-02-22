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

# || server_admin || str ||  || !WebLab-Deusto administrator's email address for notifications. See Admin Notifier settings below. ||

# || debug_mode || bool || False || If True, errors and exceptions are shown instead of generic feedback (like !WebLabInternalServerError)  ||
# || propagate_stack_traces_to_client || bool || False || If True, stacktraces are propagated to the client (useful for debugging). ||
# || facade_timeout || float || 0.5 || Seconds that the facade will wait accepting a connection before checking again for shutdown requests. ||

DEBUG_MODE                                      = 'debug_mode'

_sorted_variables.extend([
    (DEBUG_MODE, _Argument(GENERAL, bool, False, "If True, errors and exceptions are shown instead of generic feedback (like !WebLabInternalServerError)")),
])


######################################
# 
# CORE SERVER
#

CORE_SERVER = 'Core Server'


CORE = (CORE_SERVER,'General')

WEBLAB_CORE_SERVER_SESSION_TYPE     = 'core_session_type'
WEBLAB_CORE_SERVER_SESSION_POOL_ID  = 'core_session_pool_id'

_sorted_variables.extend([
    (WEBLAB_CORE_SERVER_SESSION_TYPE,    _Argument(CORE, str, 'Memory', """What type of session manager the Core Server will use: Memory or MySQL.""")),
    (WEBLAB_CORE_SERVER_SESSION_POOL_ID, _Argument(CORE, str, 'UserProcessingServer', """ A unique identifier of the type of sessions, in order to manage them. For instance, if there are four servers (A, B, C and D), the load of users can be splitted in two groups: those being sent to A and B, and those being sent to C and D. A and B can share those sessions to provide fault tolerance (if A falls down, B can keep working from the same point A was) using a MySQL session manager, and the same may apply to C and D. The problem is that if A and B want to delete all the sessions -at the beginning, for example-, but they don't want to delete sessions of C and D, then they need a unique identifier shared for A and B, and another for C and D. In this case, "!UserProcessing_A_B" and "!UserProcessing_C_D" would be enough.""")),
])

#####################################
# 
# The rest
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
                                        'default'  : variables[variable].default,
                                        'doc'      : variables[variable].message
                                    }
            print

