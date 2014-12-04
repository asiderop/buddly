from os.path import join
from sqlite3 import connect, Row

from flask import g

from buddly import app


def init():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def dump():
    with app.app_context():
        db = get_db()
        for line in db.iterdump():
            print('%s\n' % line)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect(join(app.instance_path, app.config['DATABASE']))
        db.row_factory = Row
        db.execute('PRAGMA foreign_keys = ON;')
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
