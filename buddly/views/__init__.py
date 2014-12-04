from flask import render_template, flash

from buddly import app
from buddly.db import get_db, query_db


# helper functions

def eflash(message):
    flash(message, 'error')


@app.route('/')
def index():
    sql = 'select name, description, image from event order by name desc'
    cur = get_db().execute(sql)
    entries = [dict(name=row[0], email=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=query_db(sql))

