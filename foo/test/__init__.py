import json
import os
import paste.deploy

from unittest import TestCase

from foo import model
from foo import web

_DEFAULT = object()

ENV_TEST_INI = os.environ.get('TEST_INI', 'test.ini')

HERE_DIR = os.path.dirname(os.path.abspath(__file__))
CONF_DIR = os.path.dirname(os.path.dirname(HERE_DIR))
TEST_INI = os.path.join(CONF_DIR, ENV_TEST_INI)

settings = paste.deploy.appconfig('config:' + TEST_INI)


class TestApp(TestCase):
    def setUp(self):
        super(TestApp, self).setUp()

        self.config = web.environment.setup_testing(**settings)
        self.wsgi_app = self.config.make_wsgi_app()

    def tearDown(self):
        super(TestApp, self).tearDown()


class TestModel(TestApp):
    def setUp(self):
        super(TestModel, self).setUp()
        model.create_all()


    def tearDown(self):
        model.Session.remove()


class TestWeb(TestModel):
    def setUp(self):
        super(TestWeb, self).setUp()

        from webtest import TestApp
        self.app = TestApp(self.wsgi_app)
        self.csrf_token = settings['session.constant_csrf_token']
        self.request = web.environment.Request.blank('/')

    def call_api(self, method, format='json', csrf_token=_DEFAULT, _status=None, _extra_params=None, **params):
        "Call an API method exposed by @expose_api."
        if csrf_token is _DEFAULT:
            csrf_token = self.csrf_token

        p = {
            'method': method,
            'csrf_token': csrf_token,
            'format': format,
        }
        p.update(params)
        if _extra_params:
            p.update(_extra_params)

        r = self.app.post('/api', params=p, status=_status)

        return json.loads(r.body)
