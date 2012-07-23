from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import settings

app = Flask(__name__)

#Config
app.config.from_object(settings)

conn_string = 'postgresql+psycopg2://%s:%s@%s:%d/%s' % (settings.DB_USERNAME, settings.DB_PASSWORD, 
                                               settings.DB_HOST, settings.DB_PORT,
                                               settings.DB_NAME,
                                               )

app.config['SQLALCHEMY_DATABASE_URI'] = conn_string

#Extensions
db = SQLAlchemy(app)

#neccessary imports
import weblabDeployer.views
#Import before use because we need to create the databases and to manage without running the webapp
import model.models