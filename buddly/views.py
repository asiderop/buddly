from functools import wraps
from flask import request, session, redirect, url_for, abort, render_template, flash

from buddly import app
from buddly.db import get_db, query_db


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            return redirect(url_for('login', n=request.url))
        return f(*args, **kwargs)
    return decorated_function

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

@app.route('/login', methods=['GET', 'POST'])
def login(n=None):
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['user'] = 'Bob'
            flash('You were logged in')
            url = n or url_for('show_entries')
            return redirect(url)
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

