from weblabDeployer import app
from flask import render_template, request, url_for, flash, redirect
from forms.registrationForm import RegistrationForm
from forms.loginForm import LoginForm

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data
        if email != 'slok69@gmail.com':
            flash('register first please', 'error')
            return redirect(url_for('register'))
        flash('logged', 'success')
        return redirect(url_for('index'))
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