from weblabDeployer import db

class User(db.Model):
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String)
    full_name = db.Column(db.String)
    
    token_id = db.Column(db.Integer, db.ForeignKey('tokens.id'))
    token = db.relationship('Token', backref=db.backref('User', uselist=False))
    
    def __init__(self, email, password):
        self.email = email
        self.password = password

    
class Token(db.Model):
    
    __tablename__ = 'tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    

class Entity(db.Model):
    
    __tablename__ = 'entities'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
