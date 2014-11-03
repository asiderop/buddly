from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# configuration
DATABASE = '/tmp/buddly.db'
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DATABASE)
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

db = SQLAlchemy(app)

# views/routes must be imported after creating app
import buddly.views

def init_db():
    import buddly.models
    db.create_all()

