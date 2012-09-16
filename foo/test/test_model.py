import json

from foo import test
from foo import model


class TestModel(test.TestModel):
    def test_json_serialize(self):
        u = model.User(id=1, email=u'foo@localhost.com', password_hash=u'fake_hash')

        serialized = json.loads(json.dumps({'user': u}, cls=model.meta.SchemaEncoder))

        self.assertEqual(
            serialized,
            {'user': {'id': 1, 'email': 'foo@localhost.com'}}
        )
