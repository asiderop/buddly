from uuid import uuid4 as uuid

from buddly import app, db

admin = db.Table('admin',
    db.Column('buddy_id', db.Integer, db.ForeignKey('buddy.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
)

pair = db.Table('pair',
    db.Column('santa_id', db.Integer, db.ForeignKey('buddy.id'), primary_key=True),
    db.Column('buddy_id', db.Integer, db.ForeignKey('buddy.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
)

class Buddy(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    hash  = db.Column(db.String(032), nullable=False, unique=True)

    buddies = db.relationship('Buddy',
            secondary=pair,
            foreign_keys="Buddy.id",
            primaryjoin="Buddy.id==pair.c.santa_id")

    events = db.relationship('Event',
            secondary=pair,
            foreign_keys="Buddy.id",
            primaryjoin="or_(Buddy.id==pair.c.santa_id, Buddy.id==pair.c.buddy_id)")

    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.hash = uuid().hex()

    def add_buddy(self, bud):
        self.buddies.append(bud)

    def add_event(self, ev):
        self.events.append(ev)

    def __repr__(self):
        return '<Buddy %r>' % self.name

class Event(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(120), nullable=False)
    desc  = db.Column(db.Text)
    image = db.Column(db.LargeBinary)
    date  = db.Column(db.DateTime)

    owners = db.relationship('Buddy', secondary=admin)

    def __init__(self, name, desc=None, image=None, date=None):
        self.name = name
        self.desc = desc or ''
        self.image = image
        self.date = date

    def __repr__(self):
        return '<Event %r>' % self.name

