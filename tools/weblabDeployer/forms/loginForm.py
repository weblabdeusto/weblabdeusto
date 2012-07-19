from wtforms import Form, TextField, PasswordField, validators

class LoginForm(Form):
    email = TextField('Email Address', [validators.Length(min=6, max=35), validators.Email('No es un email valido')])
    password = PasswordField('New Password', [
        validators.Required(),
    ]) 
