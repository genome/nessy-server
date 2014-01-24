from simple_lock.api import application
import simplejson
import os
import unittest


class APITest(unittest.TestCase):
    def setUp(self):
        self.app = application.create_app(
                os.environ.get('LOCKING_TEST_DB',
                    'postgres://postgres@localhost/locking_test'),
                rebuild=True)
        self.client = self.app.test_client()

    def get(self, url, **kwargs):
        return _deserialize_response(self.client.get(url, query_string=kwargs))

    def patch(self, url, data):
        return _deserialize_response(self.client.patch(url,
            content_type='application/json', data=simplejson.dumps(data)))

    def post(self, url, data):
        return _deserialize_response(self.client.post(url,
            content_type='application/json', data=simplejson.dumps(data)))

    def put(self, url, data):
        return _deserialize_response(self.client.put(url,
            content_type='application/json', data=simplejson.dumps(data)))


def _deserialize_response(response):
    try:
        response.DATA = simplejson.loads(response.data)
    except simplejson.JSONDecodeError:
        pass
    return response
