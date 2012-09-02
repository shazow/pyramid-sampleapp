from pyramid.testing import DummyRequest

from foo import test
from foo import api


class TestIndex(test.TestUnit):
    def test_hello(self):
        from foo.web.views import index
        request = DummyRequest()
        response = index.index(request)
        self.assertEqual(response['hello'], 'world')


class TestAccount(test.TestWeb):
    def test_create(self):
        response = self.app.get('/account/create', status=200)
        self.assertIn('Create account.', response)
