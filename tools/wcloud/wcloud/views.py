# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Xabier Larrakoetxea <xabier.larrakoetxea@deusto.es>
# Author: Pablo Orduña <pablo.orduna@deusto.es>
#
# These authors would like to acknowledge the Spanish Ministry of science
# and innovation, for the support in the project IPT-2011-1558-430000
# "mCloud: http://innovacion.grupogesfor.com/web/mcloud"
#

import os
import uuid
import json
import hashlib
import urlparse
import urllib2
import datetime
import StringIO

from functools import wraps

from flask import render_template, request, url_for, flash, redirect, session, abort, Response
from werkzeug import secure_filename

from weblab.admin.script import Creation, weblab_create

from wcloud import app, db, utils, deploymentsettings
from wcloud.forms import RegistrationForm, LoginForm, ConfigurationForm, DisabledConfigurationForm, DeployForm
from wcloud.models import User, Token, Entity
from wcloud.taskmanager import TaskManager

SESSION_TYPE = 'labdeployer_admin'

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        logged_in = session.get('logged_in', False)
        session_type = session.get('session_type', '')
        if not logged_in or session_type != SESSION_TYPE:
           return redirect(url_for('login', next = request.url))
        return f(*args, **kwargs)
    return decorated 


@app.route('/')
def index():
    if session.get('logged_in', False):
        return redirect(url_for('home'))
    
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        
        email = form.email.data
        password = form.password.data
        
        user = User.query.filter_by(email=email).first()
        
        #User exists?
        if user is None:
            flash('Register first please', 'error')
            return redirect(url_for('register'))
        
        #User is active
        if not user.active:
            flash("Your account isn't active. Follow the e-mail instructions. If you didn't receive it, check the SPAM directory or contact the admin at %s." % app.config['ADMIN_MAIL'], 'error')
            return redirect(url_for('index'))
        
        #If exists and is active check the password
        hash_password = hashlib.sha1(password).hexdigest()
        
        if user.password == hash_password:
            
            #Insert data in session
            session['logged_in'] = True
            session['session_type'] = SESSION_TYPE
            session['user_id'] = user.id
            session['user_email'] = user.email
            
            flash('Logged in', 'success')
            
            #Redirect
            next_url = request.args.get('next')
            if next_url != '' and next_url != None:
                return redirect(url_for(next_url))
                
            return redirect(url_for('configure'))
        else:
            flash('Failure login', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    
    form = RegistrationForm(request.form)

    if request.method == 'POST' and form.validate():
        #Exract data from the form
        full_name = form.full_name.data
        email     = form.email.data
        password  = form.password.data
        
        #create user
        user = User(email, hashlib.sha1(password).hexdigest())
        user.full_name = full_name
        user.active = False
        
        #add to database
        token = Token(str(uuid.uuid4()), datetime.datetime.now())
        user.token = token
        db.session.add(user)
        db.session.commit()
        
        #create email
        from_email = 'weblab@deusto.es'

        link = request.url_root + url_for('confirm', email=email, token=token.token)
        body_html = """ <html>
                            <head></head>
                            <body>
                              <p>Welcome!<p>
                              <p>This is the wcloud system, which creates new WebLab-Deusto instances.
                              Your account is ready, and you can activate it <a href="%s">here</a>.</p>
                              <p>If you didn't register, feel free to ignore this e-mail.</p>
                              <p>Best regards,</p>
                              <p>WebLab-Deusto team</p>
                            </body>
                          </html>""" % link
        print(body_html)
        body = """ Hello text!"""
        subject = 'thanks for registering in weblab deployer'
        
        # Send email
        try:
            utils.send_email(app, body, subject, from_email, user.email, body_html)
        except:
            db.session.delete(token)
            db.session.delete(user)
            db.session.commit()
            flash("There was an error sending the e-mail. This might be because of a invalid e-mail address. Please re-check it.", "error")
            return render_template('register.html', form=form)
        
        flash("""Thanks for registering. You have an
              email with the steps to confirm your account""", 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/confirm')
def confirm(email = None, token = None):
    if email is None:
        email = request.args.get('email')
    if token is None:
        token = request.args.get('token')

    if not email or not token:
        if not email:
            flash("Error: 'email' field misssing")
        if not token:
            flash("Error: 'token' field misssing")
        return render_template('errors.html', message="Fields missing")

    user = User.query.filter_by(email=email).first()
    
    #User exists?
    if user is None:
        flash('Register first please', 'error')
        return redirect(url_for('register'))
    #Check token
    if user.token.token != token:
        flash('Confirmation failed', 'error')
        return redirect(url_for('login'))

    #verify account
    user.active = True
    
    #update in database the active flag
    db.session.add(user)
    db.session.commit()
    
    flash('Account confirmed. Please login', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard/home')
@login_required
def home():
    email = session['user_email']
    user = User.query.filter_by(email=email).first()
    if user is None:
        return redirect(url_for('logout'))
    return render_template('home.html', user = user)


@app.route('/dashboard/configure', methods=['GET', 'POST'])
@login_required
def configure():
    email = session['user_email']
    user = User.query.filter_by(email=email).first()

    if user is None:
        flash("User not found")
        return redirect(url_for('logout'))

    if user.entity is not None and user.entity.deployed:
        enabled = False
        form = DisabledConfigurationForm(request.form)
    else:
        enabled = True
        form = ConfigurationForm(request.form)

    if user.entity is not None and user.entity.logo is not None:
        logo_available = True
    else:
        logo_available = False

    if request.method == 'POST' and form.validate():
        if not enabled:
            flash("You can not change the entity once deployed.")
            return render_template('configuration.html', form=form, enabled=enabled,logo_available=logo_available)

        # Exract data from the form
        logo = request.files['logo']
        logo_data = logo.stream.read()
        logo_ext = (logo.name or '').split('.')[-1]
        if len(logo_ext) not in (3,4):
            # That's not an extension
            logo_ext  = 'jpeg'
        name = form.name.data
        base_url = form.base_url.data
        link_url = form.link_url.data
        google_analytics_number = form.google_analytics_number.data
               
        logo_available = True

        # Create entity
        if user.entity is None:
            entity = Entity(name, base_url)
            entity.logo = logo_data
            entity.logo_ext = logo_ext
            entity.link_url = link_url
            entity.google_analytics_number = google_analytics_number
            user.entity = entity
        
        # Update
        else:
            if logo_data is not None and logo_data != '': 
                user.entity.logo = logo_data
                user.entity.logo_ext = logo_ext
            if name is not None : user.entity.name = name
            if base_url is not None : user.entity.base_url = base_url
            if link_url is not None : user.entity.link_url = link_url
            if google_analytics_number is not None :
                user.entity.google_analytics_number = google_analytics_number
            
        # Save
        db.session.add(user)
        db.session.commit()
     
        flash('Configuration saved.', 'success')
        
        if request.form.get('action','') == 'savedeploy':
            return redirect(url_for('deploy'))

    else:
         # Get user
        email = session['user_email']
        user = User.query.filter_by(email=email).first()
        if user is None:
            return redirect(url_for('logout'))
        entity = user.entity
        if entity is not None:
            form.name.data = entity.name
            form.base_url.data = entity.base_url
            form.link_url.data = entity.link_url
            form.google_analytics_number.data = entity.google_analytics_number
    return render_template('configuration.html', form=form, enabled=enabled, logo_available=logo_available)


@app.route('/dashboard/logo')
@login_required
def logo():
    email = session['user_email']
    user = User.query.filter_by(email=email).first()
    entity = user.entity
    if entity is None or entity.logo is None:
        return abort(404)
    return Response(entity.logo, headers = {'Content-Type' : 'image/%s' % entity.logo_ext})

@app.route('/dashboard/deploy', methods=['GET', 'POST'])
@login_required
def deploy():
    form = DeployForm(request.form)

    # Get user settings
    email = session['user_email']
    user = User.query.filter_by(email=email).first()
    entity = user.entity

    enabled = not user.entity.deployed

    base_url = app.config['PUBLIC_URL']
    # TODO
    # base_url += '/w/'
    base_url += '/'

    if request.method == 'POST' and form.validate():
        if not enabled:
            flash("You have already deployed your system, so you can not redeploy it")
            return render_template('deploy.html', form=form, enabled = enabled)

        admin_user = form.admin_user.data
        admin_name = form.admin_name.data
        admin_email = form.admin_email.data
        admin_password = form.admin_password.data
            
        if entity is None:
            flash('Configure before using the deployment app', 'error')
            return redirect(url_for('configure'))
        
        entity.deployed = True
        db.session.add(entity)
        db.session.commit()

        # Deploy
        
        directory = os.path.join(app.config['DIR_BASE'], entity.base_url)
               
        task = {'directory'      : directory,
                'email'          : email,
                'admin_user'     : admin_user,
                'admin_name'     : admin_name,
                'admin_email'    : admin_email,
                'admin_password' : admin_password,
                'url_root'       : base_url }
    
        task_json = json.dumps(task)

        url = "http://127.0.0.1:%s/task/" % app.config['TASK_MANAGER_PORT']
        req = urllib2.Request(url,
                            task_json,
                            {'Content-Type': 'application/json',
                             'Content-Length': len(task_json)})
        f = urllib2.urlopen(req)
        response = f.read()
        f.close()
        return redirect(url_for('result', deploy_id = response))
    
    return render_template('deploy.html', form=form, enabled=enabled, url = base_url + entity.base_url)

@app.route('/dashboard/deploy/result/<deploy_id>')
@login_required
def result(deploy_id):
    try:
        url = "http://127.0.0.1:%s/task/%s/" % (app.config['TASK_MANAGER_PORT'], deploy_id)
        req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        response = f.read()
        f.close()
    except Exception as e:
        flash(u"Error retrieving data from task manager: %s" % unicode(e), 'error')
        return render_template('result.html', stdout='Not available')

    loop = True
    response = json.loads(response)
    if response.get('status') == TaskManager.STATUS_FINISHED:
        return redirect(url_for('result_ready', deploy_id=deploy_id))
    elif response.get('status') == TaskManager.STATUS_ERROR:
        loop = False
        flash("Deployment failed. Contact the administrator")

    return render_template('result.html',
                           status=response.get('status', 'Task not found'),
                           stdout=response.get('output', 'Not available'),
                           deploy_id = deploy_id, loop = loop)

@app.route('/dashboard/deploy/ready/<deploy_id>')
@login_required
def result_ready(deploy_id):
    try:
        url = "http://127.0.0.1:%s/task/%s/" % (app.config['TASK_MANAGER_PORT'], deploy_id)
        req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        response = f.read()
        f.close()
    except Exception as e:
        flash(u"Error retrieving data from task manager: %s" % unicode(e), 'error')
        return render_template('result.html', stdout='Not available')

    response = json.loads(response)
    if response.get('status') != TaskManager.STATUS_FINISHED:
        return redirect(url_for('result', deploy_id=deploy_id))

    return render_template('result-ready.html',
                           status=response.get('status', 'Task not found'),
                           stdout=response.get('output', 'Not available'),
                           deploy_id = deploy_id, url = response.get('url', ''))


@app.route('/logout')
@login_required
def logout():
    #Insert data in session    
    session.pop('logged_in', None)
    session.pop('session_type', None)
    session.pop('user_id', None)
    session.pop('user_email', None)
    
    flash('Logged out', 'success')
    return redirect(url_for('index'))
