import os
import paste.deploy

from unittest import TestCase
from pyramid import testing

from foo import model
from foo import web


ENV_TEST_INI = os.environ.get('TEST_INI', 'test.ini')

HERE_DIR = os.path.dirname(os.path.abspath(__file__))
CONF_DIR = os.path.dirname(os.path.dirname(HERE_DIR))
TEST_INI = os.path.join(CONF_DIR, ENV_TEST_INI)

settings = paste.deploy.appconfig('config:' + TEST_INI)


class TestApp(TestCase):
    def setUp(self):
        self.wsgi_app = web.environment.setup({}, **settings)


class TestModel(TestApp):
    def setUp(self):
        super(TestModel, self).setUp()
        model.metadata.create_all(bind=model.Session.bind)


    def tearDown(self):
        model.Session.remove()


class TestUnit(TestModel):
    def setUp(self):
        super(TestUnit, self).setUp()
        self.config = testing.setUp()


    def tearDown(self):
        super(TestUnit, self).tearDown()
        testing.tearDown()


class TestWeb(TestModel):
    def setUp(self):
        super(TestWeb, self).setUp()

        from webtest import TestApp
        self.app = TestApp(self.wsgi_app)
