from uuid import uuid4 as uuid
from collections import defaultdict
from sqlite3 import IntegrityError
from time import time, localtime, asctime
from random import seed, randint

from buddly.db import query_db, get_db
from buddly import app


class ApplicationError(Exception):
    pass


class BaseModel(object):
    pass


class Buddy(BaseModel):

    def __init__(self, name, email, id_=None, hash_=None, bio=None):

        self.id_ = id_  # if None, let db assign id
        self.hash_ = hash_ or uuid().hex  # if NULL, create new hash

        self.name = name
        self.email = email
        self.bio = bio

        # { Event : [ Buddy, ] }
        self.buddies = defaultdict(list)

    def __eq__(self, other):
        return self.id_ == other.id_

    def __hash__(self):
        return hash(self.hash_)

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
        sql = 'SELECT event.* FROM event' \
              ' JOIN event_to_buddies as map' \
              ' WHERE map.buddy_id = ?' \
              '   AND map.event_id = event.id_'

        if self.buddies is None or from_db:
            self.buddies = defaultdict(list)
            rows = query_db(sql, [self.id_])
            for row in rows:
                unused = self.buddies[Event(**row)]

        return self.buddies.keys()

    def get_buddies(self, from_db=False):
        sql = 'SELECT buddy.* from buddy' \
              ' JOIN pair' \
              ' WHERE pair.santa_id = ?' \
              '   AND pair.event_id = ?' \
              '   AND pair.buddy_id = buddy.id_'

        if self.buddies is None or from_db:
            events = self.get_events(from_db)
            for ev in events:
                rows = query_db(sql, [self.id_, ev.id_])
                for row in rows:
                    b = Buddy(**row)
                    self.buddies[ev].append(b)

        return self.buddies.values()

    def get_restrictions(self):
        sql = 'SELECT buddy.* from buddy' \
              ' JOIN restrictions' \
              ' WHERE restrictions.santa_id = ?' \
              '   AND restrictions.buddy_id = buddy.id_'

        result = []
        rows = query_db(sql, [self.id_])
        for row in rows:
            result.append(Buddy(**row))

        return result

    def commit(self):
        try:
            with get_db():
                if self.id_ is None:
                    # new buddy
                    sql = 'INSERT INTO buddy (hash_, name, email, bio) VALUES (?, ?, ?, ?)'
                    cur = get_db().execute(sql, (self.hash_, self.name, self.email, self.bio))

                    self.id_ = cur.lastrowid

                    sql = 'INSERT INTO restrictions (santa_id, buddy_id) VALUES (?, ?)'
                    cur = get_db().execute(sql, (self.id_, self.id_))

                else:
                    # existing buddy
                    sql = 'UPDATE buddy SET hash_ = ?, name = ?, email = ?, bio = ? WHERE ? = id_'
                    cur = get_db().execute(sql, (self.hash_, self.name, self.email, self.bio, self.id_))

        except IntegrityError:
            raise


class Event(BaseModel):
    def __init__(self, name, description=None, image=None, start_date=None, id_=None, num_per_santa=None):
        self.id_ = id_   # if None, let db assign id
        self.name = name
        self.description = description or ''
        self.image = image
        self.start_date = start_date
        self.num_per_santa = num_per_santa

        # [ Buddy, ]
        self.owners = []
        self.buddies = []

    def __repr__(self):
        return '<Event %r>' % self.name

    @property
    def date(self):
        if self.start_date is not None:
            return asctime(localtime(self.start_date))
        return ''

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

    def start(self):
        assert self.id_ is not None
        assert self.num_per_santa in range(1, len(self.buddies))

        # 1. validate the event

        if self.start_date is not None:
            raise ApplicationError('event has already started?')

        if len(self.buddies) < 3:
            raise ApplicationError('event must have at least three buddies!')

        # 2. assign secret santas

        seed()  # make sure this is random

        # { santa : buddy }
        assigned = {}
        santas = set(self.buddies[:])
        buddies = set(self.buddies[:])

        while len(santas) > 0:
            assert len(santas) == len(buddies)
            # pick (and remove) santa from remaining list
            s = santas.pop()

            # remove invalid buddy assignments from available buddy list;
            # randomly pick buddy from list
            available = list(buddies - set(s.get_restrictions()))
            app.logger.debug('available buddies for {}: {}'.format(s, available))
            b = available[randint(0, len(available) - 1)]
            buddies.remove(b)

            # make sure last santa is not assigned themselves;
            # note: only pop santa/buddy off lists if making assignment
            if len(santas) == 1:
                assert len(buddies) == 1
                s_last = list(santas)[0]  # peak at last santa
                if s_last in buddies:
                    assigned[santas.pop()] = b  # assign buddy to last santa
                    b = buddies.pop()  # pop last buddy from list

            # validate and save assignment
            assert s != b
            assigned[s] = b

        assert 0 == len(santas) == len(buddies)
        assert len(assigned) == (self.num_per_santa * len(self.buddies))

        # 3. commit results
        with get_db():
            sql = 'INSERT INTO pair (santa_id, buddy_id, event_id) VALUES (?, ?, ?)'
            pairs = [(santa.id_, buddy.id_, self.id_) for (santa, buddy) in assigned.items()]
            get_db().executemany(sql, pairs)

            sql = 'UPDATE event SET start_date = ? WHERE ? = id_'
            cur = get_db().execute(sql, (time(), self.id_))

    def commit_new(self):
        assert self.id_ is None

        if len(self.buddies) < 1:
            raise ApplicationError('event must have at least one buddy')
        if len(self.owners) < 1:
            raise ApplicationError('event must have at least one owner')

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
