from weblabDeployer import db

class User(db.Model):
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String)
    full_name = db.Column(db.String)
    
    token_id = db.Column(db.Integer, db.ForeignKey('tokens.id'))
    token = db.relationship('Token', cascade="all, delete-orphan",
                                single_parent=True,
                                uselist=False, #This 
                                backref=db.backref('user', uselist=False)) #and this are for one-to-one

    entity_id = db.Column(db.Integer, db.ForeignKey('entities.id'))
    entity = db.relationship('Entity', backref=db.backref('users')) #many-to-one
     
    def __init__(self, email, password):
        self.email = email
        self.password = password