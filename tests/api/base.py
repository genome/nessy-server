from simple_lock.api import application
import simplejson
import unittest


class APITest(unittest.TestCase):
    def setUp(self):
        self.app = application.create_app('sqlite:///:memory:')
        self.client = self.app.test_client()

    def patch(self, url, data):
        return self.client.patch(url, content_type='application/json',
                data=simplejson.dumps(data))

    def post(self, url, data):
        return self.client.post(url, content_type='application/json',
                data=simplejson.dumps(data))

    def put(self, url, data):
        return self.client.put(url, content_type='application/json',
                data=simplejson.dumps(data))
