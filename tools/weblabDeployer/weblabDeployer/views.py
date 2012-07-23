from weblabDeployer import app
from flask import render_template, request, url_for, flash, redirect
from forms.forms import RegistrationForm, LoginForm
from model.models import User
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
            
        #If exists check the password
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