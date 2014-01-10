import redis
import time
import unittest

from libs import lock


class ExclusiveLockNoContentionTest(unittest.TestCase):
    def setUp(self):
        self.connection = redis.Redis()
        self.connection.flushall()

    def test_get_released_lock(self):
        lock_name = 'foo'

        secret = lock.get_lock(self.connection, lock_name)
        self.assertIsNotNone(secret)
        lock.release_lock(self.connection, lock_name, secret)

        new_secret = lock.get_lock(self.connection, lock_name)
        self.assertIsNotNone(new_secret)
        self.assertNotEqual(secret, new_secret)
        lock.release_lock(self.connection, lock_name, new_secret)

    def test_release_invalid_secret(self):
        lock_name = 'foo'

        secret = lock.get_lock(self.connection, lock_name)
        self.assertIsNotNone(secret)

        invalid_secret = 'INVALID_PREFIX_' + secret
        with self.assertRaises(RuntimeError):
            lock.release_lock(self.connection, lock_name, invalid_secret)

    def test_release_expired_lock(self):
        lock_name = 'foo'

        secret = lock.get_lock(self.connection, lock_name, timeout=1)
        self.assertIsNotNone(secret)

        time.sleep(2)

        with self.assertRaises(RuntimeError):
            lock.release_lock(self.connection, lock_name, secret)

    def test_get_expired_lock(self):
        lock_name = 'foo'

        secret = lock.get_lock(self.connection, lock_name, timeout=1)
        self.assertIsNotNone(secret)

        time.sleep(2)
        new_secret = lock.get_lock(self.connection, lock_name, timeout=1)
        self.assertIsNotNone(new_secret)
        self.assertNotEqual(secret, new_secret)

    def test_heartbeat_valid_lock(self):
        lock_name = 'foo'

        secret = lock.get_lock(self.connection, lock_name)
        self.assertIsNotNone(secret)
        lock.heartbeat(self.connection, lock_name, secret)
        lock.release_lock(self.connection, lock_name, secret)

    def test_heartbeat_invalid_secret(self):
        lock_name = 'foo'

        secret = lock.get_lock(self.connection, lock_name)
        self.assertIsNotNone(secret)
        invalid_secret = 'INVALID_PREFIX_' + secret
        with self.assertRaises(RuntimeError):
            lock.heartbeat(self.connection, lock_name, invalid_secret)

    def test_heartbeat_expired_lock(self):
        lock_name = 'foo'

        secret = lock.get_lock(self.connection, lock_name, timeout=1)
        self.assertIsNotNone(secret)
        time.sleep(2)
        with self.assertRaises(RuntimeError):
            lock.heartbeat(self.connection, lock_name, secret)

    def test_get_two_locks(self):
        lock_name_a = 'foo'
        lock_name_b = 'bar'

        secret_a = lock.get_lock(self.connection, lock_name_a)
        self.assertIsNotNone(secret_a)

        secret_b = lock.get_lock(self.connection, lock_name_b)
        self.assertIsNotNone(secret_b)

        lock.release_lock(self.connection, lock_name_a, secret_a)
        lock.release_lock(self.connection, lock_name_b, secret_b)


#class ExclusiveLockContentionTest(unittest.TestCase):
#    def setUp(self):
#        self.connection = redis.Redis()
#        self.connection.flushall()


if __name__ == '__main__':
    unittest.main()
