from simple_lock.api import application
import unittest


class APITest(unittest.TestCase):
    def setUp(self):
        self.app = application.create_app('sqlite:///:memory:')
        self.client = self.app.test_client()
