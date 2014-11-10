from functools import wraps
from flask import request, session, redirect, url_for, abort, render_template, flash
from sqlite3 import IntegrityError

from buddly import app, mail
from buddly.db import get_db, query_db
from buddly.models import Buddy


####################
## Authentication

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            return redirect(url_for('login', n=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    message = None
    if request.method == 'POST':
        if 'action' not in request.form:
            error = 'bad request'

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
                    error = 'a user with that email address already exists'

            elif 'remind' == action:
                b = Buddy.from_db(email=email)
                if b is None:
                    error = 'unknown email address'

            else:
                error = 'unknown action'

            if error is None:
                # send email
                return send_signup_email(b, action)

    return render_template('signup.html', error=error)


def send_signup_email(buddy, action):
    from flask_mail import Message

    error = None
    message = None
    assert isinstance(buddy, Buddy)

    msg = Message("Hello", recipients=["alexander@thequery.net"])
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

    session['user'] = b.name
    session['hash_'] = b.hash_
    flash('You were logged in')
    url = n or url_for('show_entries')
    return redirect(url)


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


####################
##

@app.route('/')
def show_entries():
    sql = 'select name, email from buddy order by name desc'
    cur = get_db().execute(sql)
    entries = [dict(name=row[0], email=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=query_db(sql))


@app.route('/add', methods=['POST'])
@login_required
def add_entry():
    get_db().execute('insert into buddy (name, email) values (?, ?)',
                 [request.form['name'], request.form['email']])
    get_db().commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

