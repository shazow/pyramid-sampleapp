import json

from foo import test
from foo import model


Session = model.Session


class TestAccount(test.TestWeb):
    def test_user_password(self):
        """ Test for a bug where the hash isn't getting encoded properly. """
        u = model.User.create(email='foo@localhost.com')
        u.set_password('foo')
        self.assertGreater(len(u.password_hash), 64)
        self.assertTrue(u.compare_password('foo'))
        Session.commit()

        u = model.User.get(1)
        self.assertGreater(len(u.password_hash), 64)
        self.assertTrue(u.compare_password('foo'))


    def test_create(self):
        r = self.app.get('/account/create', status=200)
        self.assertIn('Create account.', r.body)

        bad_params = {'method': 'account.create'}

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
        }

        r = self.app.post('/account/create', params=good_params, status=302)
        self.assertEqual(1, Session.query(model.User).count())

        u = model.User.get(1)
        self.assertTrue(u.compare_password(good_params['password']))
        self.assertEqual(u.email, good_params['email'])

        good_params['email'] = 'foo2@localhost.com'
        r = self.app.post('/api', params=good_params, status=200)
        data = json.loads(r.body)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(2, Session.query(model.User).count())

        u = model.User.get(2)
        self.assertTrue(u.compare_password(good_params['password']))
        self.assertEqual(u.email, good_params['email'])
