import json
import types
import datetime
import traceback
import threading

from functools import wraps
from collections import OrderedDict

from flask import Flask, request, Response

from voodoo.log import log, level, log_exc, logged
from weblab.comm.codes import WEBLAB_GENERAL_EXCEPTION_CODE
import weblab.configuration_doc as configuration_doc

# TODO: clean these imports
import weblab.core.login.exc as LoginErrors
import weblab.core.exc as coreExc
import weblab.exc as WebLabErrors
import voodoo.gen.exceptions.exceptions as VoodooErrors
import weblab.login.comm.codes as LFCodes
import weblab.core.comm.codes as UPFCodes

def simplify_response(response, limit = 15, counter = 0):
    """
    Recursively serializes the response into a JSON dictionary. Because the response object could actually
    contain cyclic references, we limit the maximum depth.
    """
    if counter == limit:
        return None
    if isinstance(response, (basestring, int, long, float, bool)):
        return response
    if isinstance(response, (list, tuple)):
        new_response = []
        for i in response:
            new_response.append(simplify_response(i, limit, counter + 1,))
        return new_response
    if isinstance(response, dict):
        new_response = {}
        for i in response:
            new_response[i] = simplify_response(response[i], limit, counter + 1)
        return new_response
    if isinstance(response, (datetime.datetime, datetime.date, datetime.time)):
        return response.isoformat()
    ret = {}
    for attr in [ a for a in dir(response) if not a.startswith('_') ]:
        if not hasattr(response.__class__, attr):
            attr_value = getattr(response, attr)
            if not isinstance(attr_value, types.FunctionType) and not isinstance(attr_value, types.MethodType):
                ret[attr] = simplify_response(attr_value, limit, counter + 1)
    return ret

EXCEPTIONS = (
        #
        # EXCEPTION                                   CODE                                           PROPAGATE TO CLIENT
        #
        (LoginErrors.InvalidCredentialsError, LFCodes.CLIENT_INVALID_CREDENTIALS_EXCEPTION_CODE,     True),
        (LoginErrors.LoginError,              LFCodes.LOGIN_SERVER_EXCEPTION_CODE,                   False),
        (coreExc.SessionNotFoundError,        UPFCodes.CLIENT_SESSION_NOT_FOUND_EXCEPTION_CODE,      True),
        (coreExc.NoCurrentReservationError,   UPFCodes.CLIENT_NO_CURRENT_RESERVATION_EXCEPTION_CODE, True),
        (coreExc.UnknownExperimentIdError,    UPFCodes.CLIENT_UNKNOWN_EXPERIMENT_ID_EXCEPTION_CODE,  True),
        (coreExc.WebLabCoreError,             UPFCodes.UPS_GENERAL_EXCEPTION_CODE,                   False),
        (WebLabErrors.WebLabError,            UPFCodes.WEBLAB_GENERAL_EXCEPTION_CODE,                False),
        (VoodooErrors.GeneratorError,         UPFCodes.VOODOO_GENERAL_EXCEPTION_CODE,                False),
        (Exception,                           UPFCodes.PYTHON_GENERAL_EXCEPTION_CODE,                False)

    )

for i, (exc, _, _) in enumerate(EXCEPTIONS):
    for exc2, _, _ in EXCEPTIONS[i + 1:]:
        if issubclass(exc2, exc):
            raise AssertionError("In Facade Exceptions the order is important. There can't be any exception that is a subclass of a previous exception. In this case %s is before %s" % (exc, exc2))


UNEXPECTED_ERROR_MESSAGE_TEMPLATE               = "Unexpected error ocurred in WebLab-Deusto. Please contact the administrator at %s"
SERVER_ADMIN_EMAIL                              = 'server_admin'
DEFAULT_SERVER_ADMIN_EMAIL                      = '<server_admin not set>'

def _raise_exception(code, msg):
    formatted_exc = traceback.format_exc()
    propagate = _global_context.current_weblab.ctx.config.get_doc_value(configuration_doc.PROPAGATE_STACK_TRACES_TO_CLIENT)
    if propagate:
        msg = str(msg) + "; Traceback: " + formatted_exc

    if request.args.get('indent'):
        indent = 4
    else:
        indent = None
    return Response(json.dumps({ 'is_exception' : True, 'code' : 'JSON:' + code, 'message' : msg }, indent = indent), mimetype = 'application/json')

def check_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            weblab = _global_context.current_weblab
            config = weblab.ctx.config
            weblab_class = weblab.ctx.server_instance
            for exc, code, propagate in EXCEPTIONS:
                if issubclass(e.__class__, exc):
                    if propagate or config.get_doc_value(configuration_doc.DEBUG_MODE):
                        log(weblab_class, level.Info,
                                "%s raised on %s: %s: %s" % ( exc.__name__, func.__name__, e, e.args))
                        log_exc(weblab_class, level.Debug)
                        return _raise_exception(code, e.args[0])
                    else:
                        # WebLabInternalServerError
                        log(weblab_class, level.Warning,
                                "Unexpected %s raised on %s: %s: %s" % ( exc.__name__, func.__name__, e, e.args))
                        log_exc(weblab_class, log.level.Info)
                        return _raise_exception(RemoteFacadeManagerCodes.WEBLAB_GENERAL_EXCEPTION_CODE, UNEXPECTED_ERROR_MESSAGE_TEMPLATE % config.get_value(SERVER_ADMIN_EMAIL, DEFAULT_SERVER_ADMIN_EMAIL) )

    return wrapper

def get_json():
    if request.json is not None:
        return request.json
    else:
        try:
            if request.data:
                data = request.data
            else:
                keys = request.form.keys() or ['']
                data = keys[0]
            return json.loads(data)
        except:
            log(__name__, level.Warning, "Error retrieving JSON contents")
            log_exc(__name__, level.Info)
            return None

_global_context = threading.local()

class WebLab(object):
    def __init__(self):
        self.methods = OrderedDict() # {
        #   method_name : function
        #}
        self.routes = OrderedDict() # {
        #   path : (func, path, methods)
        # }
        self.context = threading.local()
        self.ctx = self.context # Alias

    def __enter__(self):
        _global_context.current_weblab = self
        self.context.config = self.context.server_instance._cfg_manager
        
        self.context.headers = request.headers
        self.context.client_address = request.headers.get('X-Forwarded-For') or ('<unknown client. retrieved from %s>' % request.remote_addr)
        self.context.ip_address = request.headers.get('X-Forwarded-For') or ('<unknown client. retrieved from %s>' % request.remote_addr)
        self.context.user_agent = request.user_agent.string
        referer = request.referrer or ''
        self.context.referer = referer
        self.context.locale  = request.headers.get('weblabdeusto-locale', '')
        if request.headers.get('weblabdeusto-client') == 'weblabdeusto-web-mobile':
            self.context.is_mobile = True
        else:
            self.context.is_mobile = referer.find('mobile=true') >= 0 or referer.find('mobile=yes') >= 0
        self.context.is_facebook = referer.find('facebook=true') >= 0 or referer.find('facebook=yes') >= 0

        if not hasattr(self.context, 'reservation_id'):
            reservation_id = request.headers.get('X-WebLab-reservation-id')
            if not reservation_id:
                reservation_id = request.args.get('reservation_id')
            self.context.reservation_id = reservation_id
        
        if not hasattr(self.context, 'session_id'):
            session_id = request.headers.get('X-WebLab-session-id')
            if not session_id:
                session_id = request.cookies.get('weblabsessionid')
                if session_id:
                    if '.' in session_id:
                        session_id = session_id.split('.')[0]
                else:
                    session_id = request.args.get('session_id')

            self.context.session_id = session_id
    
    def __exit__(self, *args, **kwargs):
        pass

    @property
    def user_agent(self):
        return getattr(self.context, 'user_agent', '<user agent not found>')

    @property
    def reservation_id(self):
        return getattr(self.context, 'reservation_id')

    @property
    def headers(self):
        return getattr(self.context, 'headers')

    @property
    def referer(self):
        return getattr(self.context, 'referer')

    @property
    def locale(self):
        return getattr(self.context, 'locale')

    @property
    def is_mobile(self):
        return getattr(self.context, 'is_mobile')

    @property
    def is_facebook(self):
        return getattr(self.context, 'is_facebook')

    @property
    def session_id(self):
        return getattr(self.context, 'session_id')

    @property
    def ip_address(self):
        return getattr(self.context, 'ip_address')

    @property
    def config(self):
        return getattr(self.context, 'config')

    @property
    def client_address(self):
        return getattr(self.context, 'client_address')

    @property
    def server_instance(self):
        return getattr(self.context, 'server_instance')

    @property
    def app(self):
        return getattr(self.context, 'app')

    def __call__(self, server_instance = None, session_id = None, reservation_id = None):
        # To be able to run:
        # with weblab(session_id = 'foo'):
        #      something
        if session_id:
            self.context.session_id = session_id
        if reservation_id:
            self.context.reservation_id = reservation_id
        if server_instance:
            self.context.server_instance = server_instance
        return self

    def _error(self, msg, code):
        return {"message": msg, "code": code, "is_exception": True}

    def _wrap_response(self, response):
        if isinstance(response, Response):
            return response
        return self.jsonify(response)

    def _json(self, flask_app, server_instance):
        if request.method == 'POST':
            contents = get_json()
            if contents:
                method = contents['method']
                if method not in self.methods:
                    return json.dumps(msg = "Method not recognized", code = WEBLAB_GENERAL_EXCEPTION_CODE)
                parameters = contents.get('params', {})

                if 'session_id' in parameters:
                    session_id = parameters.pop('session_id')
                    if isinstance(session_id, dict) and 'id' in session_id:
                        session_id = session_id['id']
                    self.context.session_id = session_id
                    # elif: if you receive (session_id='foo', reservation_id='bar'), don't use reservation_id
                    # this happens in get_experiment_use_by_id, for example
                elif 'reservation_id' in parameters:
                    reservation_id = parameters.pop('reservation_id')
                    if isinstance(reservation_id, dict) and 'id' in reservation_id:
                        reservation_id = reservation_id['id']
                    self.context.reservation_id = reservation_id

                self.context.app = flask_app
                self.context.server_instance = server_instance
                with self:
                    return self._wrap_response(self.methods[method](**parameters))
            else:
                # TODO
                return "Not a valid JSON..."
        else:
            # TODO
            return "Hi there. This should be a list of services or something (%s)..." % ', '.join(self.methods)
        
    def route(self, path, methods = ['GET'], exc = True, logging = True, log_level = level.Info, dont_log = None, max_log_size = None):
        def wrapper(func):
            @wraps(func)
            def wrapped(*args, **kwargs):
                # TODO: DEPRECATE THIS: IN THE FUTURE, EVERYTHING ARE DICTS
                args_dict = [ simplify_response(arg) for arg in args ]
                kwargs_dict = dict(( (k, simplify_response(v)) for k, v in kwargs.iteritems() ))
                return func(*args_dict, **kwargs_dict)

            wrapped_func = wrapped
            logged_kwargs = {'is_class_method' : False}
            if dont_log:
                logged_kwargs['except_for'] = dont_log
            if max_log_size is not None:
                logged_kwargs['max_size'] = max_log_size
            logged_decorator = logged(log_level, **logged_kwargs)
            wrapped_func = logged_decorator(wrapped_func)

            if exc:
                exc_func = check_exceptions(wrapped_func)
            else:
                exc_func = wrapped_func

            if func.__name__ in self.methods:
                log(WebLab, level.Error, "Overriding %s" % func.__name__)

            self.methods[func.__name__] = exc_func
            if path in self.routes:
                log(WebLab, level.Error, "Overriding %s" % path)
            self.routes[path] = (exc_func, path, methods)
            return wrapped_func
        return wrapper

    def jsonify(self, obj, limit = 15, wrap_ok = True):
        simplified_obj = simplify_response(obj, limit = limit)
        if wrap_ok:
            simplified_obj = {
                'result' : simplified_obj,
                'is_exception' : False
            }
        indent = request.args.get('indent', None)
        if indent:
            indent = 4
        serialized = json.dumps(simplified_obj, indent = indent)
        return Response(serialized, mimetype = 'application/json') 

    def apply_routes(self, flask_app, base_path = '', server_instance = None):
        if base_path == '/':
            base_path = ''
        flask_app.route(base_path + "/", methods = ['GET', 'POST'])(lambda : self._json(flask_app, server_instance) )
        for path in self.routes:
            self._create_wrapper(base_path, path, flask_app, server_instance)

    def _create_wrapper(self, base_path, path, flask_app, server_instance):
        func, path, methods = self.routes[path]
        @wraps(func)
        def weblab_wrapper(*args, **kwargs):
            self.context.app = flask_app
            self.context.server_instance = server_instance
            with self:
                result = func(*args, **kwargs)
                return self._wrap_response(result)

        flask_app.route(base_path + path, methods = methods)(weblab_wrapper)

# weblab = WebLab()
# 
# @weblab.route("/laboratories/", methods = ['GET', 'POST'])
# def list_laboratories():
#     print weblab.context.reservation_id
#     return "Listing laboratories..."
# 
# @weblab.route("/uses/", methods = ['GET', 'POST'])
# def list_uses():
#     print weblab.context.reservation_id
#     return json.dumps([ 'use_id1', 'use_id2' ])
# 
# @weblab.route("/uses/<id>/", methods = ['GET', 'POST'])
# def list_use(id):
#     print weblab.context.reservation_id
#     return "Uses of id: %s" % id
# 
# 
# # Later on
# app = Flask(__name__)
# weblab.apply_routes(app)
# 
# # TO TEST:
# # >>> import json
# # >>> requests.post("http://localhost:5000/", data = json.dumps({'method' : 'list_uses' })).json()
# # [u'use_id1', u'use_id2']
# # >>> requests.post("http://localhost:5000/", data = json.dumps({'method' : 'list_use', 'arguments' : {'id' : 'use_id1'} })).text
# # u'Uses of id: use_id1'
# 
# 
# app.run(debug = True)
