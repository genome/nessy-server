from simple_lock.api import wsgi
import unittest


class APITest(unittest.TestCase):
    def setUp(self):
        self.client = wsgi.app.test_client()
