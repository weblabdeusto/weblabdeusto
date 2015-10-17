from __future__ import print_function, unicode_literals
import os
import sys
import json
import types
import urllib
import hashlib
import urlparse
import datetime
import traceback
import threading

from babel import Locale
from functools import wraps, partial
from collections import OrderedDict

from flask import request, Response, make_response, url_for

from voodoo.log import log, level, log_exc, logged
import weblab.core.codes as ErrorCodes
import weblab.configuration_doc as configuration_doc

# TODO: clean these imports
import weblab.core.login.exc as LoginErrors
import weblab.core.exc as coreExc
import weblab.exc as WebLabErrors
import voodoo.exc as VoodooErrors

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
        (VoodooErrors.VoodooError,         ErrorCodes.VOODOO_GENERAL_EXCEPTION_CODE,                False),
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
                        log_exc(weblab_class, level.Info)
                        return _raise_exception(ErrorCodes.WEBLAB_GENERAL_EXCEPTION_CODE, UNEXPECTED_ERROR_MESSAGE_TEMPLATE % config.get_value(SERVER_ADMIN_EMAIL, DEFAULT_SERVER_ADMIN_EMAIL) )

    return wrapper

def get_json():
    rv = request.get_json(force=True, silent=True)
    if rv:
        return rv
    
    data = request.data
    print("Error: could not deserialize:", data, file=sys.stderr)
    sys.stderr.flush()
    log(__name__, level.Warning, "Error retrieving JSON contents")
    log(__name__, level.Warning, data)
    log_exc(__name__, level.Info)
    return None

_global_context = threading.local()
DEFAULT = object()

class APIProxy(object):
    def __init__(self, methods):
        self._methods = methods

    def __getattr__(self, name):
        if name in self._methods:
            return self._methods[name]

        raise AttributeError("%s not found" % name)

class WebLabAPI(object):
    """
    The WebLabAPI object encapsulates the APIs for login, experiments, web client, etc.
    Due to the need to support two styles for calling the API, most methods to the
    actual API are dynamically added to the object and can be accessed through
    WebLabAPI.api.

    Some of the methods that are currently being added dynamically to the WebLab API object
    (which are actually added through other modules, indirectly specified in the web_contexts):
        WebLabAPI.api.login
        WebLabAPI.api.logout
        WebLabAPI.api.reserve_experiment
        WebLabAPI.api.poll
        ...
    """

    def __init__(self, web_contexts = None, api_contexts = None):
        """
        Constructs the WebLabAPI object.

        :param web_contexts: Name of the web components to register. The name will be used to generate some methods
            such as apply_routes_contextname().
        :type web_contexts: [str]

        :param api_contexts: ?
        :type api_contexts:
        """
        self.apis = set(api_contexts or ()).union(['api'])
        self.web_contexts = set(web_contexts or ()).union(self.apis)

        self.raw_methods = {}
        self.methods = {} 
        self.routes = {}
        self.context = threading.local()
        self.ctx = self.context # Alias

        for web_context in self.web_contexts:
            self.raw_methods[web_context] = {
                # method_name : function
            }

            if hasattr(self, web_context):
                raise Exception("Invalid context name: %s. Name already used as attribute." % web_context)

            if hasattr(WebLabAPI, web_context):
                raise Exception("Invalid context name: %s. Name already used in the class." % web_context)

            setattr(self, web_context, APIProxy(self.raw_methods[web_context]))

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
        for key in dir(self.context):
            if not key.startswith('__'):
                try:
                    delattr(self.context, key)
                except AttributeError:
                    pass

    @property
    def client_config(self):
        """ Check in context. If not there, retrieve from the database and store in context """
        if hasattr(self.context, 'client_config'):
            return getattr(self.context, 'client_config')
        db = self.db
        if db is None:
            return None
        client_config = db.client_configuration()
        self.context.client_config = client_config
        return client_config

    def client_property(self, name):
        client_config = self.client_config
        if client_config is None:
            return None
        return client_config.get(name)

    @property
    def current_user(self):
        """
        :rtype: weblab.db.models.DbUser
        """
        current_user = getattr(self.context, 'current_user', None)
        if current_user is not None:
            return current_user

        if getattr(self.context, 'current_user_not_found', False):
            return None
        
        try:
            user = self.api.get_user()
        except coreExc.SessionNotFoundError:
            self.context.current_user_not_found = True
            return None
        else:
            self.context.current_user = user
            return user

    @property
    def current_user_preferences(self):
        """
        :rtype: weblab.db.models.DbUserPreferences
        """
        current_user_preferences = getattr(self.context, 'current_user_preferences', None)
        if current_user_preferences is not None:
            return current_user_preferences

        if getattr(self.context, 'current_user_preferences_not_found', False):
            return None
        
        try:
            preferences = self.api.get_user_preferences()
        except coreExc.SessionNotFoundError:
            self.context.current_user_preferences_not_found = True
            return None
        else:
            self.context.current_user_preferences = preferences
            return preferences

    @property
    def is_admin(self):
        if hasattr(self.context, 'is_admin'):
            return self.context.is_admin
        
        try:
            is_admin = self.api.is_admin()
        except coreExc.SessionNotFoundError:
            is_admin = False
        self.context.is_admin = is_admin
        return self.context.is_admin

    @property
    def is_instructor(self):
        if hasattr(self.context, 'is_instructor'):
            return self.context.is_instructor
        
        try:
            is_instructor = self.api.is_instructor()
        except coreExc.SessionNotFoundError:
            is_instructor = False
        self.context.is_instructor = is_instructor
        return self.context.is_instructor


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
    def core_server_url(self):
        return self.context.config.get_value('core_server_url', None)

    @property
    def deployment_dir(self):
        return os.path.abspath(self.context.config.get_value('deployment_dir', '.'))

    @property
    def languages(self):
        if self.server_instance.babel is None:
            return []
        translations = [Locale('en')] + list(self.server_instance.babel.list_translations())
        return sorted(translations, key=lambda locale: locale.display_name.capitalize())

    @property
    def language_links(self):
        language_links = []
        for language in self.languages:
            if '?' in request.url and 'locale=' in request.url.split('?')[1]:
                # If there is already a locale= in the URL, just replace that query variable
                old_lang = request.url.split('locale=')[1].split('&')[0]
                link = request.url.replace('locale=' + old_lang, 'locale=' + language.language)
            else:
                # Otherwise, add the locale
                separator = '&' if '?' in request.url else '?'
                link = request.url + separator + 'locale=' + language.language

            language_links.append({
                'link' : link,
                'name' : language.display_name.capitalize()
            })
        return language_links

    @property
    def gravatar_url(self):
        """
        Returns the gravatar URL 
        :return: gravatar URL
        :rtype: unicode
        """
        # TODO: default to the /avatar/ thing; change the db to support that 
        # /weblab/web/avatars/<hidden-id>.jpg is that URL if the user doesn't 
        # have any gravatar URL

        # Retrieve user information
        if self.current_user:
            email = self.current_user.email

            size = 50 # To be configured

            # Calculate the Gravatar from the mail
            gravatar_url = "//www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
            gravatar_url += urllib.urlencode({'d': url_for('core_web.avatar', login=self.current_user.login, size=size, _external=True), 's': str(size)})
            return gravatar_url
        return None


    @property
    def server_instance(self):
        return getattr(self.context, 'server_instance', None)

    @property
    def app(self):
        return getattr(self.context, 'app', None)

    @property
    def db(self):
        return getattr(self.context, 'db', None)

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
            db = server_instance._db_manager,
        )

    def _error(self, msg, code):
        return {"message": msg, "code": code, "is_exception": True}

    def _wrap_response(self, response):
        if isinstance(response, Response):
            return response
        return self.wl_jsonify(response)

    def _json(self, web_context, flask_app, instance_args):
        _global_context.current_weblab = self
        self.context.config = instance_args['config']

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

                def context_retriever():
                    ctxt_info = []
                    if self.reservation_id:
                        ctxt_info.append("reservation_id={0}".format((self.reservation_id or '').split(';')[0]))
                    if self.session_id:
                        ctxt_info.append("session_id={0}".format(self.session_id))
                    if ctxt_info:
                        return ';'.join(ctxt_info)
                    return ''
                logged_kwargs['ctxt_retriever'] = context_retriever
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
            self.raw_methods[web_context][func.__name__] = wrapped_func
            return wrapped_func
        return wrapper

    def jsonify(self, **kwargs):
        obj = kwargs
        indent = request.args.get('indent', None)
        if indent:
            indent = 4
        serialized = json.dumps(obj, indent = indent)
        response = Response(serialized, mimetype = 'application/json')

        if self.session_id:
            session_id_cookie = '%s.%s' % (self.session_id, self.ctx.route)
            self.fill_session_cookie(response, session_id_cookie)

        return response
       

    def wl_jsonify(self, obj, limit = 15, wrap_ok = True):
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

    def make_response(self, *args, **kwargs):
        response = make_response(*args, **kwargs)
        if self.session_id:
            self.fill_session_cookie(response)
        return response

    def fill_session_cookie(self, response, value = None):
        """
        Inserts the weblabsessionid and loginweblabsessionid cookies into the specified Flask response.
        :type response: flask.wrappers.Response
        :type value: str
        :return: The flask response with the added cookies.
        :rtype: flask.wrappers.Response
        """
        if value is None:
            value = '%s.%s' % (self.session_id, self.ctx.route)
            
        now = datetime.datetime.utcnow()
        response.set_cookie('weblabsessionid', value, expires = now + datetime.timedelta(days = 100), path = self.ctx.location)
        response.set_cookie('loginweblabsessionid', value, expires = now + datetime.timedelta(hours = 1), path = self.ctx.location)
        return response

    def apply_routes(self, web_context, flask_app, server_instance = None, base_path = ''):
        if base_path == '/':
            base_path = ''

        instance_args = self._get_instance_args(server_instance, flask_app)

        if web_context in self.apis:
            flask_app.route(base_path + "/", methods = ['GET', 'POST'], endpoint = 'service_url')(lambda : self._json(web_context, flask_app, instance_args) )

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

