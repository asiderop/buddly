from flask import Flask

# extensions
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail, email_dispatched


class Config(object):
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2mb
    SERVER_NAME = 'buddly.local:5000'     # host name (with port)
    SECRET_KEY = 'MUST BE OVERRIDDEN'     # unique value
    DATABASE = 'buddly.db'                # in instance folder


    # mail config
    MAIL_DEFAULT_SENDER = 'buddly-no-reply'


class DebugConfig(Config):
    DEBUG = True
    SECRET_KEY = 'development key'

    # debug toolbar config
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class TestConfig(Config):
    TESTING = True


# create our little application :)
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('buddly.Config')
app.config.from_pyfile('application.cfg', silent=True)

# add debug toolbar (only when app.debug is True)
toolbar = DebugToolbarExtension(app)

# create Mail instance for sending emails
mail = Mail(app)

if app.testing:
    def log_message(message, app):
        app.logger.debug(message)

    email_dispatched.connect(log_message)

# views/routes should be the last thing imported (i.e. after creating app)
import buddly.views
import buddly.views.authentication
import buddly.views.buddy
import buddly.views.event
