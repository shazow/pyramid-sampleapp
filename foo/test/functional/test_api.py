import json

from foo import test


class TestApi(test.TestWeb):
    def test_ping(self):
        r = self.app.post('/api', params={'method': 'ping', 'csrf_token': 'TESTING_CSRF'})
        data = json.loads(r.body)

        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['result'], {'ping': 'pong'})
