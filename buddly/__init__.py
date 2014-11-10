from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

# configuration
DATABASE = '/tmp/buddly.db'
DEBUG = True
SECRET_KEY = 'development key'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

app.debug = True
app.config['SECRET_KEY'] = '<replace with a secret key>'

toolbar = DebugToolbarExtension(app)

# views/routes must be imported after creating app
import buddly.views

