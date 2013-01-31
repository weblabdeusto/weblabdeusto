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
import hashlib
import uuid
import StringIO
from functools import wraps
import json
import urllib2

from flask import render_template, request, url_for, flash, redirect, session
from werkzeug import secure_filename
from weblab.admin.script import Creation, weblab_create

from wlcloud import app, db, utils, deploymentsettings
from wlcloud.forms import RegistrationForm, LoginForm, \
                            ConfigurationForm, DeployForm
from wlcloud.models import User, Token, Entity

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
            flash('register first please', 'error')
            return redirect(url_for('register'))
        
        #User is active
        if not user.active:
            flash('Your account isn\'t active', 'error')
            return redirect(url_for('index'))
        
        #If exists and is active check the password
        hash_password = hashlib.sha1(password).hexdigest()
        
        if user.password == hash_password:
            
            #Insert data in session
            session['logged_in'] = True
            session['session_type'] = SESSION_TYPE
            session['user_id'] = user.id
            session['user_email'] = user.email
            
            flash('logged', 'success')
            
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
        email = form.email.data
        password = form.password.data
        
        #create user
        user = User(email, hashlib.sha1(password).hexdigest())
        user.full_name = full_name
        user.active = False
        
        #add to database
        token = Token(str(uuid.uuid4()))
        user.token = token
        db.session.add(user)
        db.session.commit()
        
        #create email
        from_email = 'weblab@deusto.es'
        link = 'http://%s/confirm?email=%s&token=%s' % (request.host, email, token.token)
        body_html = """ <html>
                            <head></head>
                            <body>
                              <p>Hi!<br>
                                 Thank you for registering<br>
                                 Here is the <a href="%s">link</a> for \
                                    confirming your account.
                              </p>
                            </body>
                          </html>""" % link
        print(body_html)
        body = """ Hello text!"""
        subject = 'thanks for registering in weblab deployer'
        
        #send email
        utils.send_email(body, subject, from_email, user.email, body_html)
        
        flash("""Thanks for registering. You have an
              email with the steps to confirm your account""", 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/confirm')
def confirm():
    
    email = request.args.get('email')
    token = request.args.get('token')
    
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
            entity.end_port_number = 9999 #start in 10000
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
        
    else:
         # Get user
        email = session['user_email']
        user = User.query.filter_by(email=email).first()
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
        
        
        task = {'directory': directory,
                'email': email,
                'admin_user': admin_user,
                'admin_name': admin_name,
                'admin_email': admin_email,
                'admin_password': admin_password,}
    
        task_json = json.dumps(task)
        url = "http://127.0.0.1:1661/task"
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
    url = "http://127.0.0.1:1661/task/%s/stdout" % deploy_id
    req = urllib2.Request(url)
    f = urllib2.urlopen(req)
    response = f.read()
    f.close()

    return render_template('result.html',
                           stdout=response,
                           deploy_id = deploy_id)


@app.route('/logout')
@login_required
def logout():
    #Insert data in session    
    session.pop('logged_in', None)
    session.pop('session_type', None)
    session.pop('user_id', None)
    session.pop('user_email', None)
    
    flash('logout', 'success')
    return redirect(url_for('index'))
