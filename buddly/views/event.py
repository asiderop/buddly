from flask import request, session, render_template, flash

from buddly import app
from buddly.models import Buddy, Event
from buddly.forms import EventCreation, EventBuddies
from buddly.views.authentication import login_required

@app.route('/event/<id_>', methods=['GET'])
@app.route('/event/', methods=['GET', 'POST'])
@login_required
def event(id_=None):
    from base64 import b64encode
    from wand.image import Image

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
                form.name.data,
                form.description.data,
                base64_image)

            owner = Buddy.from_db(hash_=session.get('hash_'))
            assert owner is not None
            e.buddies.append(owner)
            e.owners.append(owner)
            e.commit()

            flash('Thanks for creating. {}'.format(e.id_))

    return render_template('event-create.html', form=form)


@app.route('/event/<id_>/buddies', methods=['GET', 'POST'])
@login_required
def event_buddies(id_):
    err = None
    e = Event.from_db(id_)
    if e is None:
        return render_template('event-buddy.html', form=None, event=None, error='unknown event')

    form = EventBuddies()
    if request.method == 'POST':
        if form.validate():
            buddy = Buddy.from_db(email=form.email.data)
            if buddy is None:
                buddy = Buddy(name=form.name.data, email=form.email.data)
                buddy.commit()
            e.buddies.append(buddy)
            e.commit()

            form = EventBuddies()
            flash('Buddy added to event.')

    return render_template('event-buddy.html', form=form, event=e, error=err)
