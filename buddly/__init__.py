from os import getenv

from flask import Flask

# extensions
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail, email_dispatched


class Config(object):
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2mb
    SERVER_NAME = 'buddly.local:5000'     # host name (with port)
    SECRET_KEY = 'MUST BE OVERRIDDEN'     # unique value
    DATABASE = 'buddly.db'                # in instance folder
    DEBUG = False

    ADMINS = [
        'admin@%s' % SERVER_NAME,
    ]

    # mail config
    MAIL_DEFAULT_SENDER = 'buddly-no-reply@%s' % SERVER_NAME


class DebugConfig(Config):
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'development key'

    # debug toolbar config
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class TestConfig(Config):
    TESTING = True


# create our little application :)
app = Flask(__name__, instance_relative_config=True)

# set configuration values
if getenv('BUDDLY_DEBUG', False):
    app.config.from_object('buddly.DebugConfig')
elif getenv('BUDDLY_TEST', False):
    app.config.from_object('buddly.TestConfig')
else:
    app.config.from_object('buddly.Config')
app.config.from_pyfile('buddly.cfg', silent=True)

assert app.config['SECRET_KEY'] != Config.SECRET_KEY, "you must override the SECRET_KEY"

# add debug toolbar (only when app.debug is True)
toolbar = DebugToolbarExtension(app)

# create Mail instance for sending emails
mail = Mail(app)

if app.testing:
    def log_message(message, app):
        app.logger.debug(message)

    email_dispatched.connect(log_message)

if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('127.0.0.1',
                               'server-error@%s' % app.config['SERVER_NAME'],
                               app.config['ADMINS'], '%s Failed' % app.name)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

# views/routes should be the last thing imported (i.e. after creating app)
import buddly.views
import buddly.views.authentication
import buddly.views.buddy
import buddly.views.event
