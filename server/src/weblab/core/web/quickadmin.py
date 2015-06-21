from flask import render_template, request, send_file, Response, url_for
from functools import wraps, partial
from weblab.core.web import weblab_api, get_argument


def check_credentials(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        expected_token = weblab_api.config.get('quickadmin_token', None)

        if expected_token:
            token = request.args.get('token')
            if not token:
                return Response("You must provide a token like ?token=something")

            if token != expected_token:
                return Response("Invalid token")

        return func(*args, **kwargs)

    return wrapper

def get_url_for():
    if 'token' in request.args:
        return partial(url_for, token = request.args['token'])
    return url_for

@weblab_api.route_web('/quickadmin/')
@check_credentials
def index():
    return render_template("quickadmin/index.html", url_for = get_url_for())

LIMIT = 200

@weblab_api.route_web('/quickadmin/uses')
@check_credentials
def uses():
    kwargs = {}
    for potential_arg in 'login', 'experiment_name', 'category_name':
        if potential_arg in request.args:
            kwargs[potential_arg] = request.args[potential_arg]
    url_for = get_url_for()
    url_for = partial(url_for, **request.args)
    return render_template("quickadmin/uses.html",  uses = weblab_api.db.quickadmin_uses(LIMIT, **kwargs), arguments = kwargs, url_for = url_for, title = 'Uses', endpoint = '.uses')

@weblab_api.route_web('/quickadmin/use/<int:use_id>')
@check_credentials
def use(use_id):
    return render_template("quickadmin/use.html", url_for = get_url_for(), **weblab_api.db.quickadmin_use(use_id = use_id))

@weblab_api.route_web('/quickadmin/file/<int:file_id>')
@check_credentials
def file(file_id):
    file_path = weblab_api.db.quickadmin_filepath(file_id = file_id)
    if file_path is None:
        return "File not found", 404

    return send_file(file_path, as_attachment = True)

@weblab_api.route_web('/quickadmin/demos')
@check_credentials
def demos():
    kwargs = {}
    for potential_arg in 'login', 'experiment_name', 'category_name':
        if potential_arg in request.args:
            kwargs[potential_arg] = request.args[potential_arg]
    url_for = get_url_for()
    url_for = partial(url_for, **request.args)
    group_names = weblab_api.config.get_value('login_default_groups_for_external_users', [])
    return render_template("quickadmin/uses.html",  uses = weblab_api.db.quickadmin_uses(LIMIT, group_names = group_names, **kwargs), arguments = kwargs, url_for = url_for, title = 'Demo uses', endpoint = '.demos')

