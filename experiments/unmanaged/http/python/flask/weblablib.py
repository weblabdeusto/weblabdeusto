import json
import redis
import datetime
from collections import namedtuple
from flask import Blueprint, jsonify, request, current_app, Response, redirect, url_for

#############################################################
# 
# WebLab-Deusto API:
# 
# First, this method creates new sessions. We store the 
# sessions on memory in this dummy example.
# 

class WebLab(object):
    def __init__(self, app = None, url = None, public_url = None):
        self._app = app
        self._url = url
        self._public_url = public_url
        self._redis_client = None

        self.provider_class = None
        self._session_id_provider = None
        self._initial_url = None
        self._session_id_name = 'weblab_session_id'

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self._app = app
        redis_url = self._app.config.get('WEBLAB_REDIS_URL', 'redis://localhost:6379/0')
        self._session_id_name = self._app.config.get('WEBLAB_SESSION_ID_NAME', 'weblab_session_id')

        provider_class = self.provider_class
        if provider_class is None:
            provider_class = redis.StrictRedis

        self._redis_client = provider_class.from_url(redis_url)
        self._app.extensions['weblab'] = self

        if self._url:
            url = '%s/weblab' % self._url
        else:
            url = '/weblab'
        
        self._app.register_blueprint(weblab, url_prefix=url)

        @self._app.route(self._public_url + '/<session_id>')
        def public_url(session_id):
            session[self._session_id_name] = session_id
            return redirect(self.initial_url())

    def _session_id(self):
        return session[self._session_id_name]
    
    def initial_url(self, func):
        self._initial_url = func
        return func

weblab = Blueprint("weblab", __name__)

def _current_weblab():
    app = current_app()
    if 'weblab' in app.extensions:
        raise Exception("App not initialized with weblab.init_app()")
    return app.extensions['weblab']

def _current_redis():
    return _current_weblab().redis_client

def _current_session_id():
    return _current_weblab()._session_id()

User = namedtuple("User", ["back", "last_poll", "max_date", "username", "exited"])
PastUser = namedtuple("PastUser", ["back"])

def current_user():
    session_id = _current_session_id()
    pipeline = _current_redis().pipeline()
    pipeline.hget("weblab:active:{}".format(session_id), "back")
    pipeline.hget("weblab:active:{}".format(session_id), "last_poll")
    pipeline.hget("weblab:active:{}".format(session_id), "max_date")
    pipeline.hget("weblab:active:{}".format(session_id), "username")
    pipeline.hget("weblab:active:{}".format(session_id), "exited")
    back, last_poll, max_date, username, exited = pipeline.execute()
    if last_poll is None:
        return None

    return User(back=back, last_poll=last_poll, max_date=max_date, username=username, exited=exited)

def past_user():
    session_id = _current_session_id()
    back = _current_redis().hget("weblab:inactive:{}".format(session_id), "back")
    if back is None:
        return None

    return PastUser(back=back)
    

# TODO: '%s' WILL NOT WORK IN WINDOWS

def _get_last_poll():
    last_poll = datetime.now()
    last_poll_int = last_poll.strftime('%s') + str(last_poll.microsecond / 1e6)[1:]
    return last_poll_int

def _renew_poll(session_id):
    last_poll_int = _get_last_poll()
    pipeline = _current_redis().pipeline()
    pipeline.hget("weblab:active:{}".format(session_id), "max_date")
    pipeline.hset("weblab:active:{}".format(session_id), "last_poll", last_poll_int)
    max_date, _ = pipeline.execute()
    if max_date is None:
        pipeline.delete("weblab:active:{}".format(session_id))

def _force_exited(session_id):
    pipeline = _current_redis().pipeline()
    pipeline.hget("weblab:active:{}".format(session_id), "max_date")
    pipeline.hset("weblab:active:{}".format(session_id), "exited", "true")
    max_date, _ = pipeline.execute()
    if max_date is None:
        pipeline.delete("weblab:active:{}".format(session_id))

def _get_time_left(session_id):
    current_time = datetime.now()
    current_time = float(current_time.strftime('%s') + str(current_time.microsecond / 1e6)[1:])

    max_date = _current_redis().hget("weblab:active:{}".format(session_id), "max_date")
    if max_date is None:
        return 0

    return float(max_date) - current_time

@weblab.before_request
def _require_http_credentials():
    # Don't require credentials in /api
    if request.url.endswith('/api'):
        return

    auth = request.authorization
    if auth:
        username = auth.username
        password = auth.password
    else:
        username = password = "No credentials"

    weblab_username = current_app.config['WEBLAB_USERNAME']
    weblab_password = current_app.config['WEBLAB_PASSWORD']
    if username != weblab_username or password != weblab_password:
        if request.url.endswith('/test'):
            return Response(json.dumps(dict(valid=False, error_messages=["Invalid credentials"])), status=401, headers = {'WWW-Authenticate':'Basic realm="Login Required"', 'Content-Type': 'application/json'})

        print("In theory this is weblab. However, it provided as credentials: {} : {}".format(username, password))
        return Response(response=("You don't seem to be a WebLab-Instance"), status=401, headers = {'WWW-Authenticate':'Basic realm="Login Required"'})

@weblab.route("/sessions/api")
def api_version():
    return jsonify(api_version="1")

@weblab.route("/sessions/test")
def test():
    return jsonify(valid=True)

@weblab.route("/sessions/", methods=['POST'])
def start_experiment():
    request_data = request.get_json(force=True)

    client_initial_data = request_data['client_initial_data']
    server_initial_data = request_data['server_initial_data']

    # Parse the initial date + assigned time to know the maximum time
    start_date_str = server_initial_data['priority.queue.slot.start']
    start_date_str, microseconds = start_date_str.split('.')
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S") + timedelta(microseconds = int(microseconds))
    max_date = start_date + timedelta(seconds = float(server_initial_data['priority.queue.slot.length']))

    # Create a global session
    session_id = str(random.randint(0, 10e8)) # Not especially secure 0:-)

    # Prepare adding this to redis
    max_date_int = max_date.strftime('%s') + str(max_date.microsecond / 1e6)[1:]
    last_poll_int = get_last_poll()
    
    pipeline = _current_redis().pipeline()
    pipeline.hset('weblab:active:{}'.format(session_id), 'max_date', max_date_int)
    pipeline.hset('weblab:active:{}'.format(session_id), 'last_poll', last_poll_int)
    pipeline.hset('weblab:active:{}'.format(session_id), 'username', server_initial_data['request.username'])
    pipeline.hset('weblab:active:{}'.format(session_id), 'back', request_data['back'])
    pipeline.hset('weblab:active:{}'.format(session_id), 'exited', 'false')
    pipeline.expire('weblab:active:{}'.format(session_id), 30 + int(float(server_initial_data['priority.queue.slot.length'])))
    pipeline.execute()
    
    kwargs = {}
    scheme = current_app.config.get('WEBLAB_SCHEME')
    if scheme:
        kwargs['_scheme'] = scheme

    link = url_for('public_url', session_id=session_id, _external = True, **kwargs)
    return jsonify(url=link, session_id=session_id)

#############################################################
# 
# WebLab-Deusto API:
# 
# This method provides the current status of a particular 
# user.
# 
@weblab.route('/sessions/<session_id>/status')
def status(session_id):
    last_poll = _current_redis().hget("weblab:active:{}".format(session_id), "last_poll")
    max_date = _current_redis().hget("weblab:active:{}".format(session_id), "max_date")
    username = _current_redis().hget("weblab:active:{}".format(session_id), "username")
    exited = _current_redis().hget("weblab:active:{}".format(session_id), "exited")
    
    if exited == 'true':
        return jsonify(should_finish= -1)

    if last_poll is not None:
        current_time = datetime.now()
        current_time = float(current_time.strftime('%s') + str(current_time.microsecond / 1e6)[1:])
        difference = current_time - float(last_poll)
        print "Did not poll in", difference, "seconds"
        if difference >= 15:
            return jsonify(should_finish=-1)

        print "User %s still has %s seconds" % (username, (float(max_date) - current_time))

        if float(max_date) <= current_time:
            print "Time expired"
            return jsonify(should_finish=-1)

        return jsonify(should_finish=5)

    print "User not found"
    # 
    # If the user is considered expired here, we can return -1 instead of 10. 
    # The WebLab-Deusto scheduler will mark it as finished and will reassign
    # other user.
    # 
    return jsonify(should_finish=-1)

#############################################################
# 
# WebLab-Deusto API:
# 
# This method is called to kick one user out. This may happen
# when an administrator defines so, or when the assigned time
# is over.
# 
@weblab.route('/sessions/<session_id>', methods=['POST'])
def dispose_experiment(session_id):
    request_data = request.get_json(force=True)
    if 'action' in request_data and request_data['action'] == 'delete':
        redis_client = _current_redis()
        back = redis_client.hget("weblab:active:{}".format(session_id), "back")
        if back is not None:
            pipeline = redis_client.pipeline()
            pipeline.delete("weblab:active:{}".format(session_id))
            pipeline.hset("weblab:inactive:{}".format(session_id), "back", back)
            # During half an hour after being created, the user is redirected to
            # the original URL. After that, every record of the user has been deleted
            pipeline.expire("weblab:inactive:{}".format(session_id), 3600)
            pipeline.execute()
            return jsonify(message="Deleted")
        return jsonify(message="Not found")
    return jsonify(message="Unknown op")
