"""
Authentication Views
"""

from sqlite3 import IntegrityError
from functools import wraps
from flask import request, session, redirect, url_for, render_template, flash

from buddly import app, mail
from buddly.models import Buddy


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('hash_'):
            return redirect(url_for('login', n=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    message = None
    if request.method == 'POST':
        if 'action' not in request.form:
            error = "Hmm, that's a bad request."

        else:
            action = request.form['action']
            email = request.form['email']
            b = None

            if 'signup' == action:
                name = request.form['name']
                b = Buddy(name, email)
                try:
                    b.commit()
                except IntegrityError:
                    error = 'Sorry, a user with that email address already exists!'

            elif 'remind' == action:
                b = Buddy.from_db(email=email)
                if b is None:
                    error = "Sorry, I don't know email address."

            else:
                error = "Sorry, I don't understand that action."

            if error is None:
                # send email
                return send_signup_email(b, action)

    return render_template('signup.html', error=error)


def send_signup_email(buddy, action):
    from flask_mail import Message

    error = None
    message = None
    assert isinstance(buddy, Buddy)

    msg = Message("Hello!", recipients=[buddy.email])
    msg.html = render_template('email-signup.html', b=buddy)
    mail.send(msg)

    if 'signup' == action:
        message = "Nice! We're sending an email to %s with all the deets." % buddy.email
    elif 'remind' == action:
        message = "Hang tight. We're sending your unique login link to %s." % buddy.email
    else:
        raise NotImplementedError()

    return render_template('signup.html', error=error, message=message, user=buddy.hash_)


@app.route('/login', methods=['GET'])
def login(n=None):
    if 'h' not in request.args:
        return render_template('login.html')

    h = request.args['h']
    b = Buddy.from_db(hash_=h)

    if b is None:
        return render_template('login.html', error='unknown user')

    session['hash_'] = b.hash_
    session['name'] = b.name  # for convenience in templates
    flash('You were logged in')
    url = n or url_for('index')
    return redirect(url)


@app.route('/logout')
def logout():
    session.pop('hash_', None)
    flash('You were logged out')
    return redirect(url_for('index'))


