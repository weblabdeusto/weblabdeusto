from weblabDeployer import db
    

class Entity(db.Model):
    
    __tablename__ = 'entities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)#. e.g. University of Deusto
    logo = db.Column(db.LargeBinary)#e.g. (the logo of the entity)
    base_url = db.Column(db.String)#e.g. /myschool.
    link_url = db.Column(db.String)#e.g. http://www.deusto.es
    google_analytics_number = db.Column(db.String)#e.g. UA-1234-1234
    
    def __init__(self, name, base_url):
        self.name = name
        self.base_url = base_url