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

from weblabDeployer import app
from flask import render_template, request, url_for, flash, redirect
from weblabDeployer.forms import RegistrationForm, LoginForm
from weblabDeployer.models import User
import hashlib
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
            next = request.args.get('next')
            if next != '':
                return redirect(url_for(next))
                
            return redirect(url_for('index'))
        else:
            flash('Failure login', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = form.username.data
        email = form.email.data
        password = form.password.data
        print('%s, %s, %s' % (user, email, password))
        flash('Thanks for registering', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)