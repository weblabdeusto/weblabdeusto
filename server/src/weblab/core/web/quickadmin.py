import datetime
from flask import render_template, request, send_file, Response, url_for
from functools import wraps, partial
from weblab.core.web import weblab_api, get_argument
from weblab.core.db import UsesQueryParams

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
    my_url_for = partial(url_for, **request.args)

    if 'token' in request.args:
        return partial(my_url_for, token = request.args['token'])
    return my_url_for

def create_query_params(**kwargs):
    params = {}
    for potential_arg in 'login', 'experiment_name', 'category_name':
        if potential_arg in request.args:
            params[potential_arg] = request.args[potential_arg]
    for potential_arg in 'start_date', 'end_date':
        if potential_arg in request.args:
            try:
                params[potential_arg] = datetime.datetime.strptime(request.args[potential_arg], "%Y-%m-%d").date()
            except ValueError:
                pass
    params.update(kwargs)
    return UsesQueryParams(**params)

def apply_map_exclusions(per_country):
    pass

@weblab_api.route_web('/quickadmin/')
@check_credentials
def index():
    return render_template("quickadmin/index.html", url_for = get_url_for())

LIMIT = 200

@weblab_api.route_web('/quickadmin/uses')
@check_credentials
def uses():
    query_params = create_query_params()
    uses = weblab_api.db.quickadmin_uses(LIMIT, query_params)
    return render_template("quickadmin/uses.html",  uses = uses, arguments = query_params.pubdict(), param_url_for = get_url_for(), title = 'Uses', endpoint = '.uses')

@weblab_api.route_web('/quickadmin/use/<int:use_id>')
@check_credentials
def use(use_id):
    return render_template("quickadmin/use.html", param_url_for = get_url_for(), **weblab_api.db.quickadmin_use(use_id = use_id))

@weblab_api.route_web('/quickadmin/file/<int:file_id>')
@check_credentials
def file(file_id):
    file_path = weblab_api.db.quickadmin_filepath(file_id = file_id)
    if file_path is None:
        return "File not found", 404

    return send_file(file_path, as_attachment = True)   

@weblab_api.route_web('/quickadmin/uses/map')
@check_credentials
def uses_map():
    query_params = create_query_params()
    per_country = weblab_api.db.quickadmin_uses_per_country(query_params)
    apply_map_exclusions(per_country)
    return render_template("quickadmin/uses_map.html", per_country = per_country, arguments = query_params.pubdict(), param_url_for = get_url_for(), title = 'Uses map', endpoint = '.uses_map')


@weblab_api.route_web('/quickadmin/demos')
@check_credentials
def demos():
    group_names = weblab_api.config.get_value('login_default_groups_for_external_users', [])
    query_params = create_query_params(group_names = group_names)
    uses = weblab_api.db.quickadmin_uses(LIMIT, query_params)
    return render_template("quickadmin/uses.html",  uses = uses, arguments = query_params.pubdict(), param_url_for = get_url_for(), title = 'Demo uses', endpoint = '.demos')

@weblab_api.route_web('/quickadmin/demos/map')
@check_credentials
def demos_map():
    group_names = weblab_api.config.get_value('login_default_groups_for_external_users', [])
    query_params = create_query_params(group_names = group_names)
    per_country = weblab_api.db.quickadmin_uses_per_country(query_params)
    apply_map_exclusions(per_country)
    return render_template("quickadmin/uses_map.html", per_country = per_country, arguments = query_params.pubdict(), param_url_for = get_url_for(), title = 'Demo uses map', endpoint = '.demos_map')

