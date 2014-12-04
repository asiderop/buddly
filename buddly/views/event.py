from sqlite3 import IntegrityError
from flask import request, session, render_template, flash, redirect, url_for

from buddly import app, eflash
from buddly.models import Buddy, Event, ApplicationError
from buddly.forms import EventCreation, EventBuddies
from buddly.views.authentication import login_required

@app.route('/event/', methods=['GET', 'POST'])
@login_required
def event_create():
    from base64 import b64encode
    from wand.image import Image

    err = None
    form = EventCreation()

    if request.method == 'POST':
        if form.validate():
            base64_image = ''

            if form.image.data:
                f = request.files[form.image.name]
                with Image(file=f.stream) as i:
                    i.transform(resize='120x120>')
                    base64_image = b64encode(i.make_blob('png'))

            e = Event(
                name=form.name.data,
                description=form.description.data,
                image=base64_image,
                num_per_santa=form.num_buddies,
                )

            owner = Buddy.from_db(hash_=session.get('hash_'))
            assert owner is not None
            e.buddies.append(owner)
            e.owners.append(owner)

            try:
                e.commit_new()
                flash('Sweet. Your event has been created.')
            except IntegrityError:
                err = 'Something went wrong. :('

    return render_template('event-create.html', form=form, error=err)


@app.route('/event/<id_>/', methods=['GET', 'POST'])
@login_required
def event_details(id_):
    err = None
    form = None

    b = Buddy.from_db(hash_=session['hash_'])
    assert b is not None

    e = Event.from_db(id_)
    if e is None:
        err = "Sorry, I don't know that event."

    is_owner = b in e.owners

    if is_owner:
        form = EventCreation()
        form.name.data = e.name
        form.description.data = e.description

        if request.method == 'POST':
            if form.validate():
                flash('Saved.')

    return render_template('event-details.html', error=err, event=e, form=form, is_owner=is_owner)


@app.route('/event/<id_>/launch', methods=['POST'])
@login_required
def event_launch(id_):

    e = Event.from_db(id_)
    if e is None:
        eflash("Sorry, I don't know that event.")

    else:
        try:
            e.start()
            flash('Your event has launched!')
        except ApplicationError as e:
            eflash("Wait, " + e.message)
        except IntegrityError as e:
            app.logger.error('IntegrityError while starting event: ' + e.message)
            eflash("Wait, an error occurred while launching event. :/")

    return redirect(url_for('event_details', id_=id_))


@app.route('/event/<id_>/buddies/', methods=['GET', 'POST'])
@login_required
def event_buddies(id_):
    err = None

    e = Event.from_db(id_)
    if e is None:
        err = "Sorry, I don't know that event."
        return render_template('event-buddy.html', error=err)

    form = EventBuddies()
    if request.method == 'POST':
        if form.validate():
            buddy = Buddy.from_db(email=form.email.data)
            if buddy is None:
                buddy = Buddy(name=form.name.data, email=form.email.data)
                buddy.commit()
            e.buddies.append(buddy)
            e.commit_new()

            form = EventBuddies()
            flash('Buddy added to event.')

    return render_template('event-buddy.html', form=form, event=e, error=err)
