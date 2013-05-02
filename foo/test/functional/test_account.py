import json

from foo import test
from foo import api
from foo import model


Session = model.Session


class TestAccount(test.TestWeb):
    def test_user_password(self):
        # Test for a bug where the hash isn't getting encoded properly.
        u = model.User.create(email=u'foo@localhost.com')
        u.set_password(u'foo')
        self.assertGreater(len(u.password_hash), 64)
        self.assertTrue(u.compare_password(u'foo'))
        Session.commit()

        u = model.User.get(1)
        self.assertGreater(len(u.password_hash), 64)
        self.assertTrue(u.compare_password(u'foo'))


    def test_create(self):
        r = self.app.get('/account/create', status=200)
        self.assertIn('Create account.', r.body)

        bad_params = {
            'method': 'account.create',
            'csrf_token': self.csrf_token,
        }

        # Test delegated API controller call fail.
        r = self.app.post('/account/create', params=bad_params, status=200)
        self.assertIn('Missing required parameter', r.body)

        # Test actual API controller call fail
        r = self.app.post('/api', params=bad_params, status=400)
        data = json.loads(r.body)
        self.assertEqual(data['status'], 'error')
        self.assertIn('Missing required parameter', data['messages'][0])

        # Test database state
        self.assertEqual(0, Session.query(model.User).count())

        # Test successes
        good_params = {
            'method': u'account.create',
            'email': u'foo@localhost.com',
            'password': u'foo',
            'password_confirm': u'foo',
            'csrf_token': self.csrf_token,
        }

        r = self.app.post('/account/create', params=good_params, status=303)
        self.assertEqual(1, Session.query(model.User).count())

        u = model.User.get(1)
        self.assertTrue(u.compare_password(good_params['password']))
        self.assertEqual(u.email, good_params['email'])

        good_params['email'] = u'foo2@localhost.com'
        r = self.app.post('/api', params=good_params, status=200)
        data = json.loads(r.body)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(2, Session.query(model.User).count())

        u = model.User.get(2)
        self.assertTrue(u.compare_password(good_params['password']))
        self.assertEqual(u.email, good_params['email'])


    def test_login(self):
        params = {
            'method': u'account.login',
            'email': u'foo@localhost.com',
            'password': u'barbaz',
            'csrf_token': self.csrf_token,
        }

        u = api.account.create(email=params['email'], password=params['password'])
        self.assertTrue(u.compare_password(params['password']))

        # Bad email
        bad_params = params.copy()
        bad_params['email'] = u'bar@localhost.com'
        self.app.post('/account/login', params=bad_params, status=200)

        # Bad password
        bad_params = params.copy()
        bad_params['password'] = u'foofoo'
        self.app.post('/account/login', params=bad_params, status=200)

        # Success
        r = self.app.post('/account/login', params=params)
        self.assertEqual(r.status_int, 303, r.body)
