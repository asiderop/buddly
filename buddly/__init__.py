from flask import Flask

# extensions
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail, email_dispatched

# configuration
DATABASE = '/tmp/buddly.db'
DEBUG = True
TESTING = True
SECRET_KEY = 'development key'

## main config
MAIL_DEFAULT_SENDER = 'buddly-no-reply'

## debug toolbar config
DEBUG_TB_INTERCEPT_REDIRECTS = False

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

# add debug toolbar (only when app.debug is True)
toolbar = DebugToolbarExtension(app)

# create Mail instance for sending emails
mail = Mail(app)

# views/routes must be imported after creating app
import buddly.views


if app.testing:
    def log_message(message, app):
        app.logger.debug(message)

    email_dispatched.connect(log_message)
