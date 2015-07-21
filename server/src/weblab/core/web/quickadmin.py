from __future__ import print_function, unicode_literals
import datetime
from flask import render_template, request, send_file, Response, url_for
from functools import wraps, partial
from weblab.core.web import weblab_api
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
    existing_args = dict(request.args)
    existing_args.pop('page', None)
    my_url_for = partial(url_for, **existing_args)

    if 'token' in request.args:
        return partial(my_url_for, token = request.args['token'])
    return my_url_for

def create_query_params(**kwargs):
    params = {}
    for potential_arg in 'login', 'experiment_name', 'category_name', 'ip', 'country':
        if potential_arg in request.args:
            params[potential_arg] = request.args[potential_arg]

    for potential_arg in 'start_date', 'end_date':
        if potential_arg in request.args:
            try:
                params[potential_arg] = datetime.datetime.strptime(request.args[potential_arg], "%Y-%m-%d").date()
            except ValueError:
                pass

    for potential_arg in 'page',:
        if potential_arg in request.args:
            try:
                params[potential_arg] = int(request.args[potential_arg])
            except ValueError:
                pass

    if 'page' not in params or params['page'] <= 0:
        params['page'] = 1

    for potential_arg in 'date_precision',:
        if potential_arg in request.args:
            if request.args[potential_arg] in ('day', 'month', 'year', 'week'):
                params[potential_arg] = request.args[potential_arg]

    if 'date_precision' not in params:
        params['date_precision'] = 'month'
                
    params.update(kwargs)
    query_params = UsesQueryParams(**params)
    metadata = weblab_api.db.quickadmin_uses_metadata(query_params)
    params['count'] = metadata['count']

    if 'start_date' in params:
        params['min_date'] = params['start_date']
    else:
        params['min_date'] = metadata['min_date']

    if 'end_date' in params:
        params['max_date'] = params['end_date']
    else:
        params['max_date'] = metadata['max_date']

    return UsesQueryParams(**params)

@weblab_api.route_web('/quickadmin/')
@check_credentials
def index():
    return render_template("quickadmin/index.html", url_for = get_url_for())

LIMIT = 20

@weblab_api.route_web('/quickadmin/uses')
@check_credentials
def uses():
    query_params = create_query_params()
    uses = weblab_api.db.quickadmin_uses(LIMIT, query_params)
    return render_template("quickadmin/uses.html", limit = LIMIT, uses = uses, filters = query_params.filterdict(), arguments = query_params.pubdict(), param_url_for = get_url_for(), title = 'Uses', endpoint = '.uses')

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
    per_time = _per_country_by_to_d3(weblab_api.db.quickadmin_uses_per_country_by(query_params))
    return render_template("quickadmin/uses_map.html", per_country = per_country, per_time = per_time, arguments = query_params.pubdict(), param_url_for = get_url_for(), title = 'Uses map', endpoint = '.uses_map')


@weblab_api.route_web('/quickadmin/demos')
@check_credentials
def demos():
    group_names = weblab_api.config.get_value('login_default_groups_for_external_users', [])
    query_params = create_query_params(group_names = group_names)
    uses = weblab_api.db.quickadmin_uses(LIMIT, query_params)
    return render_template("quickadmin/uses.html", limit = LIMIT, uses = uses, arguments = query_params.pubdict(), param_url_for = get_url_for(), title = 'Demo uses', endpoint = '.demos')

@weblab_api.route_web('/quickadmin/demos/map')
@check_credentials
def demos_map():
    group_names = weblab_api.config.get_value('login_default_groups_for_external_users', [])
    query_params = create_query_params(group_names = group_names)
    per_country = weblab_api.db.quickadmin_uses_per_country(query_params)
    per_time = _per_country_by_to_d3(weblab_api.db.quickadmin_uses_per_country_by(query_params))
    return render_template("quickadmin/uses_map.html", per_country = per_country, per_time = per_time, arguments = query_params.pubdict(), param_url_for = get_url_for(), title = 'Demo uses map', endpoint = '.demos_map')

def _per_country_by_to_d3(per_time):
    new_per_time = [
        # {
        #     key : country,
        #     values : [
        #          [
        #              time_in_milliseconds,
        #              value
        #          ]
        #     ]
        # }
    ]
    total_per_country = [
        # (country, number)
    ]
    for country in per_time:
        total_per_country.append( (country, sum([ value for key, value in per_time[country] ]) ))

    total_per_country.sort(lambda x, y: cmp(x[1], y[1]), reverse = True)
    top_countries = [ country for country, value in total_per_country[:10] ]
    max_value = max([value for country, value in total_per_country[:10] ] or [0])
    key_used = 'month'
    times_in_millis = {
        # millis : datetime
    }
    for country in top_countries:
        for key in [ key for key, value in per_time[country] ]:
            if len(key) == 1:
                if isinstance(key[0], datetime.date):
                    key_used = 'day'
                    date_key = key[0]
                else:
                    key_used = 'year'
                    date_key = datetime.date(year = key[0], month = 1, day = 1)
            elif len(key) == 2:
                key_used = 'month'
                date_key = datetime.date(year = key[0], month = key[1], day = 1)
            else:
                continue
            time_in_millis = int(date_key.strftime("%s")) * 1000
            times_in_millis[time_in_millis] = key

    for country in per_time:
        if country not in top_countries:
            continue

        country_data = {'key' : country, 'values' : []}
        country_time_data = dict(per_time[country])
        for time_in_millis in sorted(times_in_millis):
            key = times_in_millis[time_in_millis]
            value = country_time_data.get(key, 0)
            country_data['values'].append([time_in_millis, value])
        new_per_time.append(country_data)
    return { 'key_used' : key_used, 'per_time' : new_per_time, 'max_value' : max_value}

