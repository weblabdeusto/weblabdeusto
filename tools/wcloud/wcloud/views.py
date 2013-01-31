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
import urllib2
import datetime
import StringIO

from functools import wraps

from flask import render_template, request, url_for, flash, redirect, session
from werkzeug import secure_filename

from weblab.admin.script import Creation, weblab_create

from wcloud import app, db, utils, deploymentsettings
from wcloud.forms import RegistrationForm, LoginForm, ConfigurationForm, DeployForm
from wcloud.models import User, Token, Entity

SESSION_TYPE = 'labdeployer_admin'

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        logged_in = session.get('logged_in', False)
        session_type = session.get('session_type', '')
        print(session_type)
        if not logged_in or session_type != SESSION_TYPE:
           return redirect(url_for('login', next = request.url))
        return f(*args, **kwargs)
    return decorated 


@app.route('/')
def index():
    if session.get('logged_in', False):
        return redirect(url_for('configure'))
    
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
            raise
        
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


@app.route('/configure', methods=['GET', 'POST'])
@login_required
def configure():
    form = ConfigurationForm(request.form)

    if request.method == 'POST' and form.validate():
        # Exract data from the form
        logo = request.files['logo']
        logo_data = logo.stream.read()
        name = form.name.data
        base_url = form.base_url.data
        link_url = form.link_url.data
        google_analytics_number = form.google_analytics_number.data
        
        # Get user
        email = session['user_email']
        user = User.query.filter_by(email=email).first()
        
        # Create entity
        if user.entity is None:
            entity = Entity(name, base_url)
            entity.logo = logo_data
            entity.link_url = link_url
            entity.google_analytics_number = google_analytics_number
            user.entity = entity

        # Update
        else:
            if logo_data is not None : user.entity.logo = logo_data
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
            return redirect('deploy')

    else:
         # Get user
        email = session['user_email']
        user = User.query.filter_by(email=email).first()
        if user is None:
            return redirect('logout', indicate=False)
        entity = user.entity
        if entity is not None:
            form.name.data = entity.name
            form.base_url.data = entity.base_url
            form.link_url.data = entity.link_url
            form.google_analytics_number.data = entity.google_analytics_number
            
    return render_template('configuration.html', form=form)


@app.route('/deploy', methods=['GET', 'POST'])
@login_required
def deploy():
    form = DeployForm(request.form)

    if request.method == 'POST' and form.validate():
        admin_user = form.admin_user.data
        admin_name = form.admin_name.data
        admin_email = form.admin_email.data
        admin_password = form.admin_password.data
    
        # Get user settings
        email = session['user_email']
        user = User.query.filter_by(email=email).first()
        entity = user.entity
        
        if entity is None:
            flash('Configure before usinng the deployment app', 'error')
            return redirect(url_for('configure'))
        
        # Step 1, create the deployments dir if necessary
        if not os.path.exists(deploymentsettings.DIR_BASE):
            os.mkdir(deploymentsettings.DIR_BASE)
        
        # Step 2, deploy
        
        directory = os.path.join(deploymentsettings.DIR_BASE, entity.base_url)
        
        
        task = {'directory'      : directory,
                'email'          : email,
                'admin_user'     : admin_user,
                'admin_name'     : admin_name,
                'admin_email'    : admin_email,
                'admin_password' : admin_password}
    
        task_json = json.dumps(task)
        url = "http://127.0.0.1:1661/task/"
        req = urllib2.Request(url,
                            task_json,
                            {'Content-Type': 'application/json',
                             'Content-Length': len(task_json)})
        f = urllib2.urlopen(req)
        response = f.read()
        f.close()
        print('-'*50)
        print(response)
        print('-'*50)
        return redirect(url_for('result', deploy_id = response))
    
    return render_template('deploy.html', form=form)

@app.route('/deploy/result/<deploy_id>')
@login_required
def result(deploy_id):
    try:
        url = "http://127.0.0.1:1661/task/%s/output" % deploy_id
        req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        response = f.read()
        f.close()

        url = "http://127.0.0.1:1661/task/%s/status" % deploy_id
        req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        status = f.read()
        f.close()
    except Exception as e:
        flash(u"Error retrieving data from task manager: %s" % unicode(e), 'error')
        return render_template('result.html', stdout='Not available')

    return render_template('result.html',
                           status=status,
                           stdout=response,
                           deploy_id = deploy_id)


@app.route('/logout')
@login_required
def logout(indicate=True):
    #Insert data in session    
    session.pop('logged_in', None)
    session.pop('session_type', None)
    session.pop('user_id', None)
    session.pop('user_email', None)
    
    if indicate:
        flash('Logged out', 'success')
    return redirect(url_for('index'))
