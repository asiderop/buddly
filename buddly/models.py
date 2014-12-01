from uuid import uuid4 as uuid
from collections import defaultdict
from sqlite3 import IntegrityError

from buddly.db import query_db, get_db


class BaseModel(object):
    pass


class Buddy(BaseModel):

    def __init__(self, name, email, id_=None, hash_=None):

        self.id_ = id_  # if None, let db assign id
        self.hash_ = hash_ or uuid().hex  # if NULL, create new hash

        self.name = name
        self.email = email

        # { Event : [ Buddy, ] }
        self.buddies = defaultdict(list)

    def __repr__(self):
        return '<Buddy %r>' % self.name

    @classmethod
    def from_db(cls, email=None, hash_=None, id_=None):
        assert (email is not None) ^ (hash_ is not None) ^ (id_ is not None)
        # the above xor (with three operands) will result to True when all three operands are
        # True; so we specifically check against that as well
        assert (email is None) or (hash_ is None) or (id_ is None)

        sql = 'SELECT * FROM buddy ' \
              ' WHERE ? = email OR ? = hash_ OR ? = id_'
        row = query_db(sql, [email, hash_, id_], one=True)

        if row is None:
            return None

        return cls(**row)

    def get_events(self, from_db=False):
        sql = 'SELECT * FROM event' \
              ' JOIN event_to_buddies as map' \
              ' WHERE map.buddy_id = ?' \
              '   AND map.event_id = event.id_'

        if self.buddies is None or from_db:
            self.buddies = defaultdict(list)
            rows = query_db(sql, [self.id_])
            for row in rows:
                unused = self.buddies[Event(*row)]

        return self.buddies.keys()

    def get_buddies(self, from_db=False):
        sql = 'SELECT * from buddy' \
              ' JOIN pair' \
              ' WHERE pair.santa_id = ?' \
              '   AND pair.event_id = ?' \
              '   AND pair.buddy_id = buddy.id_'

        if self.buddies is None or from_db:
            events = self.get_events(from_db)
            for ev in events:
                rows = query_db(sql, [self.id_, ev.id_])
                for row in rows:
                    b = Buddy(*row)
                    self.buddies[ev].append(b)

        return self.buddies.values()

    def commit(self):
        ev_sql = 'INSERT INTO event_to_buddy (event_id, buddy_id) VALUES (?, ?)'
        bud_sql = 'INSERT INTO pair (santa_id, buddy_id, event_id) VALUES (?, ?, ?)'

        if self.id_ is None:
            try:
                with get_db():
                    # new buddy, try to insert into db
                    sql = 'INSERT INTO buddy (hash_, name, email) VALUES (?, ?, ?)'
                    cur = get_db().execute(sql, (self.hash_, self.name, self.email))

                    self.id_ = cur.lastrowid

                    '''
                    for (ev, bud_list) in self.buddies.items():
                        if ev.id_ is None:
                            raise NotImplementedError('event does not exist?')
                        get_db().execute(ev_sql, [ev.id_, self.id_])
                        for bud in bud_list:
                            if bud.id_ is None:
                                raise NotImplementedError('buddy does not exist?')
                            get_db().execute(bud_sql, [self.id_, bud.id_, ev.id_])
                    '''

            except IntegrityError:
                raise

        else:
            raise NotImplementedError('cannot do update')


class Event(BaseModel):
    def __init__(self, name, description=None, image=None, start_date=None, id_=None):
        self.id_ = id_   # if None, let db assign id
        self.name = name
        self.description = description or ''
        self.image = image
        self.start_date = start_date

        # [ Buddy, ]
        self.owners = []
        self.buddies = []

    def __repr__(self):
        return '<Event %r>' % self.name

    @classmethod
    def from_db(cls, id_):

        # lookup event
        sql = 'SELECT * FROM event ' \
              ' WHERE ? = id_'
        row = query_db(sql, [id_], one=True)

        if row is None:
            return None

        e = cls(**row)

        # lookup buddies for event
        sql = 'SELECT * FROM event_to_buddies as e2b ' \
              ' WHERE ? = e2b.event_id'
        rows = query_db(sql, [e.id_])

        for row in rows:
            b = Buddy.from_db(id_=row['buddy_id'])
            assert b is not None
            e.buddies.append(b)
            if row['is_owner']:
                e.owners.append(b)

        return e

    def commit(self):
        if self.id_ is None:
            if len(self.buddies) < 1:
                raise IntegrityError('event must have at least one buddy')
            if len(self.owners) < 1:
                raise IntegrityError('event must have at least one owner')

            for o in self.owners:
                assert o in self.buddies

            try:
                with get_db():
                    # new event, try to insert into db
                    sql = 'INSERT INTO event (name, description, image, start_date) VALUES (?, ?, ?, ?)'
                    cur = get_db().execute(sql, (self.name, self.description, self.image, self.start_date))

                    self.id_ = cur.lastrowid

                    for b in self.buddies:
                        # insert rows to map event to buddies
                        sql = 'INSERT INTO event_to_buddies (event_id, buddy_id, is_owner) VALUES (?, ?, ?)'
                        cur = get_db().execute(sql, (self.id_, b.id_, b in self.owners))

            except IntegrityError:
                raise

        else:
            raise NotImplementedError('cannot do update')
