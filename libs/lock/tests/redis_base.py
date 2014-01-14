import redis
import unittest


class RedisTest(unittest.TestCase):
    def setUp(self):
        self.connection = redis.Redis()
        self.connection.flushall()
