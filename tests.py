import os
import unittest
import tempfile

import buddly.db as db
from buddly import app


class BuddlyTestCase(unittest.TestCase):

    fakehash = 'fakehashfortest'
    fakename = 'Test Dummy'
    fakemail = 'test@dummy.com'

    def setUp(self):
        app.config['TESTING'] = True
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        self.app = app.test_client()
        db.init()

        with app.app_context():
            with db.get_db():
                sql = 'INSERT INTO buddy (hash_, name, email) VALUES (?, ?, ?)'
                db.query_db(sql, [self.fakehash, self.fakename, self.fakemail])

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def login(self, hash_):
        return self.app.get('/login', query_string={'h': hash_}, follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    ##################################
    ## test cases

    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'No events here so far.' in rv.data

    def test_login_logout(self):
        rv = self.login(self.fakehash)
        assert 'You were logged in.' in rv.data
        rv = self.logout()
        assert 'You were logged out.' in rv.data
        rv = self.login('badhash')
        assert 'unknown user' in rv.data

    def test_messages(self):
        self.login(self.fakehash)
        rv = self.app.post('/add', data=dict(
            name='<Hello>',
            email='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert 'No entries here so far' not in rv.data
        assert '&lt;Hello&gt;' in rv.data
        assert '<strong>HTML</strong> allowed here' in rv.data


if __name__ == '__main__':
    unittest.main()

