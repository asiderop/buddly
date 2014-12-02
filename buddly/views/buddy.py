from sqlite3 import IntegrityError
from flask import request, session, render_template, flash

from buddly import app
from buddly.models import Buddy
from buddly.forms import BuddyProfile
from buddly.views.authentication import login_required

@app.route('/buddy/<id_>', methods=['GET', 'POST'])
@app.route('/buddy/', methods=['GET', 'POST'])
@login_required
def profile(id_=None):
    err = None

    if id_ is None:
        b = Buddy.from_db(hash_=session['hash_'])
    else:
        b = Buddy.from_db(id_=id_)

    if b is None:
        return render_template('buddy-profile.html', error="Sorry, I don't know that user.")

    form = BuddyProfile()
    if request.method == 'POST':
        if form.validate():
            b.name = form.name.data
            b.email = form.email.data
            b.bio = form.bio.data
            try:
                b.commit()
                session['user'] = b.name
                flash('Changes saved.')
            except IntegrityError:
                err = "Hmm, looks like that someone else is using that email address."

    else:
        form.name.data = b.name
        form.email.data = b.email
        form.bio.data = b.bio


    return render_template('buddy-profile.html', form=form, buddy=b, error=err)
