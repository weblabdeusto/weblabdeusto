from weblabDeployer import db


class Token(db.Model):
    
    __tablename__ = 'tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, unique=True)
    
    def __init__(self, token):
        self.token = token