import json
import types
import urlparse
import datetime
import traceback
import threading

from functools import wraps, partial
from collections import OrderedDict

from flask import request, Response

from voodoo.log import log, level, log_exc, logged
import weblab.core.codes as ErrorCodes
import weblab.configuration_doc as configuration_doc

# TODO: clean these imports
import weblab.core.login.exc as LoginErrors
import weblab.core.exc as coreExc
import weblab.exc as WebLabErrors
import voodoo.gen.exceptions.exceptions as VoodooErrors

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
        (LoginErrors.InvalidCredentialsError, ErrorCodes.CLIENT_INVALID_CREDENTIALS_EXCEPTION_CODE,     True),
        (LoginErrors.LoginError,              ErrorCodes.LOGIN_SERVER_EXCEPTION_CODE,                   False),
        (coreExc.SessionNotFoundError,        ErrorCodes.CLIENT_SESSION_NOT_FOUND_EXCEPTION_CODE,      True),
        (coreExc.NoCurrentReservationError,   ErrorCodes.CLIENT_NO_CURRENT_RESERVATION_EXCEPTION_CODE, True),
        (coreExc.UnknownExperimentIdError,    ErrorCodes.CLIENT_UNKNOWN_EXPERIMENT_ID_EXCEPTION_CODE,  True),
        (coreExc.WebLabCoreError,             ErrorCodes.UPS_GENERAL_EXCEPTION_CODE,                   False),
        (WebLabErrors.WebLabError,            ErrorCodes.WEBLAB_GENERAL_EXCEPTION_CODE,                False),
        (VoodooErrors.GeneratorError,         ErrorCodes.VOODOO_GENERAL_EXCEPTION_CODE,                False),
        (Exception,                           ErrorCodes.PYTHON_GENERAL_EXCEPTION_CODE,                False)

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

    try:
        msg = unicode(msg)
    except:
        msg = u"Message could not be decoded"

    response = Response(json.dumps({ 'is_exception' : True, 'code' : 'JSON:' + code, 'message' : msg }, indent = indent), mimetype = 'application/json')
    return response

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
                        return _raise_exception(ErrorCodes.WEBLAB_GENERAL_EXCEPTION_CODE, UNEXPECTED_ERROR_MESSAGE_TEMPLATE % config.get_value(SERVER_ADMIN_EMAIL, DEFAULT_SERVER_ADMIN_EMAIL) )

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
DEFAULT = object()

class WebLabAPI(object):
    def __init__(self, web_contexts = None, api_contexts = None):
        self.apis = set(api_contexts or ()).union(['api'])
        self.web_contexts = set(web_contexts or ()).union(self.apis)

        self.methods = {} 
        self.routes = {}
        for web_context in self.web_contexts:
            self.methods[web_context] = OrderedDict() # {
            #   method_name : function
            #}

            self.routes[web_context] = OrderedDict() # {
            #   path : (func, path, methods)
            # }

            route_method = partial(self.route, web_context)
            setattr(self, 'route_%s' % web_context, route_method)

            apply_routes_method = partial(self.apply_routes, web_context)
            setattr(self, 'apply_routes_%s' % web_context, apply_routes_method)

        self.context = threading.local()
        self.ctx = self.context # Alias

    def __enter__(self):
        _global_context.current_weblab = self
        
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
            if not reservation_id:
                reservation_id = request.cookies.get('weblab_reservation_id')
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
        return getattr(self.context, 'reservation_id', None)

    @property
    def headers(self):
        return getattr(self.context, 'headers', None)

    @property
    def referer(self):
        return getattr(self.context, 'referer', None)

    @property
    def locale(self):
        return getattr(self.context, 'locale', None)

    @property
    def is_mobile(self):
        return getattr(self.context, 'is_mobile', None)

    @property
    def is_facebook(self):
        return getattr(self.context, 'is_facebook', None)

    @property
    def session_id(self):
        return getattr(self.context, 'session_id', None)

    @property
    def ip_address(self):
        return getattr(self.context, 'ip_address', None)

    @property
    def config(self):
        return getattr(self.context, 'config', None)

    @property
    def client_address(self):
        return getattr(self.context, 'client_address', None)

    @property
    def server_instance(self):
        return getattr(self.context, 'server_instance', None)

    @property
    def app(self):
        return getattr(self.context, 'app', None)

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
            for name, value in self._get_instance_args(server_instance, None).iteritems():
                setattr(self.context, name, value)

        return self

    def _get_instance_args(self, server_instance, flask_app):
        config = server_instance._cfg_manager
        core_server_url = config.get_value( 'core_server_url', '' )

        return dict(
            config = config,
            app = flask_app,
            server_instance = server_instance,
            core_server_url = core_server_url,
            location = urlparse.urlparse(core_server_url).path or '/weblab/',
            route = server_instance._server_route,
        )

    def _error(self, msg, code):
        return {"message": msg, "code": code, "is_exception": True}

    def _wrap_response(self, response):
        if isinstance(response, Response):
            return response
        return self.jsonify(response)

    def _json(self, web_context, flask_app, instance_args):
        if request.method == 'POST':
            contents = get_json()
            if contents:
                if 'method' not in contents:
                    return _raise_exception(code = ErrorCodes.WEBLAB_GENERAL_EXCEPTION_CODE, msg = "Missing 'method' attr")
                method = contents['method']
                if method not in self.methods[web_context]:
                    return _raise_exception(code = ErrorCodes.WEBLAB_GENERAL_EXCEPTION_CODE, msg = "Method not recognized")
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

                for name, value in instance_args.iteritems():
                    setattr(self.context, name, value)

                with self:
                    return self._wrap_response(self.methods[web_context][method](**parameters))
            else:
                return _raise_exception(ErrorCodes.WEBLAB_GENERAL_EXCEPTION_CODE, "Couldn't deserialize message")
        else:
            response = """<html>
            <head>
                <title>WebLab-Deusto JSON service</title>
            </head>
            <body>
                Welcome to the WebLab-Deusto service through JSON. Available methods:
                <ul>
            """

            for method_name in self.methods[web_context]:
                method = self.methods[web_context][method_name]
                response += """<li><b>%s</b>: %s</li>\n""" % (method_name, method.__doc__ or '')

            response += """</ul>
            </body>
            </html>
            """
            return response
        
    def route(self, web_context, path, methods = ['GET'], exc = DEFAULT, logging = DEFAULT, log_level = level.Info, dont_log = None, max_log_size = None):
        def wrapper(func):
            @wraps(func)
            def wrapped(*args, **kwargs):
                # TODO: DEPRECATE THIS: IN THE FUTURE, EVERYTHING ARE DICTS
                args_dict = [ simplify_response(arg) for arg in args ]
                kwargs_dict = dict(( (k, simplify_response(v)) for k, v in kwargs.iteritems() ))
                return func(*args_dict, **kwargs_dict)

            if logging == DEFAULT:
                must_log = web_context in self.apis
            else:
                must_log = logging

            if exc == DEFAULT:
                capture_exc = web_context in self.apis
            else:
                capture_exc = exc

            wrapped_func = wrapped
            if must_log:
                logged_kwargs = {'is_class_method' : False}
                if dont_log:
                    logged_kwargs['except_for'] = dont_log
                if max_log_size is not None:
                    logged_kwargs['max_size'] = max_log_size
                logged_decorator = logged(log_level, **logged_kwargs)
                wrapped_func = logged_decorator(wrapped_func)

            if capture_exc:
                exc_func = check_exceptions(wrapped_func)
            else:
                exc_func = wrapped_func

            if func.__name__ in self.methods[web_context]:
                log(WebLabAPI, level.Error, "Overriding %s" % func.__name__)

            self.methods[web_context][func.__name__] = exc_func
            if path in self.routes[web_context]:
                log(WebLabAPI, level.Error, "Overriding %s" % path)
            self.routes[web_context][path] = (exc_func, path, methods)
            self.routes[web_context][path] = (exc_func, path, methods)
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
        response = Response(serialized, mimetype = 'application/json')

        if self.session_id:
            session_id_cookie = '%s.%s' % (self.session_id, self.ctx.route)
            self.fill_session_cookie(response, session_id_cookie)

        return response

    def fill_session_cookie(self, response, value):
        now = datetime.datetime.now()
        response.set_cookie('weblabsessionid', value, expires = now + datetime.timedelta(days = 100), path = self.ctx.location)
        response.set_cookie('loginweblabsessionid', value, expires = now + datetime.timedelta(hours = 1), path = self.ctx.location)
        return response

    def apply_routes(self, web_context, flask_app, server_instance = None, base_path = ''):
        if base_path == '/':
            base_path = ''

        instance_args = self._get_instance_args(server_instance, flask_app)

        if web_context in self.apis:
            flask_app.route(base_path + "/", methods = ['GET', 'POST'])(lambda : self._json(web_context, flask_app, instance_args) )
        for path in self.routes[web_context]:
            self._create_wrapper(base_path, path, flask_app, web_context, instance_args)

    def _create_wrapper(self, base_path, path, flask_app, web_context, instance_args):
        func, path, methods = self.routes[web_context][path]

        @wraps(func)
        def weblab_wrapper(*args, **kwargs):
            for name, value in instance_args.iteritems():
                setattr(self.context, name, value) 
            with self:
                result = func(*args, **kwargs)
                if web_context in self.apis:
                    result = self._wrap_response(result)
                
                return result

        flask_app.route(base_path + path, methods = methods)(weblab_wrapper)

