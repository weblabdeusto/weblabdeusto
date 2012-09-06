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

from weblabDeployer import app, db, utils
from flask import render_template, request, url_for, flash, redirect, session
from weblabDeployer.forms import RegistrationForm, LoginForm, ConfigurationForm
from weblabDeployer.models import User, Token, Entity
from werkzeug import secure_filename
import hashlib
import uuid
from functools import wraps


SESSION_TYPE = 'labdeployer_admin'

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
                
            return redirect(url_for('index'))
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

@login_required
@app.route('/configure', methods=['GET', 'POST'])
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
