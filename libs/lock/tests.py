import redis
import time
import unittest

from libs import lock
from libs.lock import exceptions


class ExclusiveLockNoContentionTest(unittest.TestCase):
    def setUp(self):
        self.connection = redis.Redis()
        self.connection.flushall()

    def test_get_released_lock(self):
        lock_name = 'foo'

        request_id = lock.get_lock(self.connection, lock_name,
                timeout_seconds=1)
        self.assertIsNotNone(request_id)
        lock.release_lock(self.connection, lock_name, request_id)

        new_request_id = lock.get_lock(self.connection, lock_name,
                timeout_seconds=1)
        self.assertIsNotNone(new_request_id)
        self.assertNotEqual(request_id, new_request_id)
        lock.release_lock(self.connection, lock_name, new_request_id)

    def test_release_invalid_request_id(self):
        lock_name = 'foo'

        request_id = lock.get_lock(self.connection, lock_name,
                timeout_seconds=1)
        self.assertIsNotNone(request_id)

        invalid_request_id = 'INVALID_PREFIX_' + request_id
        with self.assertRaises(exceptions.RequestIdMismatch):
            lock.release_lock(self.connection, lock_name, invalid_request_id)

    def test_release_expired_lock(self):
        lock_name = 'foo'

        request_id = lock.get_lock(self.connection, lock_name,
                timeout_seconds=1)
        self.assertIsNotNone(request_id)

        time.sleep(2)

        with self.assertRaises(exceptions.NonExistantLock):
            lock.release_lock(self.connection, lock_name, request_id)

    def test_heartbeat_extends_ttl(self):
        lock_name = 'foo'

        request_id = lock.get_lock(self.connection, lock_name,
                timeout_seconds=3)
        self.assertIsNotNone(request_id)
        time.sleep(2)

        lock.heartbeat(self.connection, lock_name, request_id)
        time.sleep(2)
        lock.release_lock(self.connection, lock_name, request_id)


    def test_get_expired_lock(self):
        lock_name = 'foo'

        request_id = lock.get_lock(self.connection, lock_name,
                timeout_seconds=1)
        self.assertIsNotNone(request_id)

        time.sleep(2)
        new_request_id = lock.get_lock(self.connection, lock_name,
                timeout_seconds=1)
        self.assertIsNotNone(new_request_id)
        self.assertNotEqual(request_id, new_request_id)

    def test_heartbeat_valid_lock(self):
        lock_name = 'foo'

        request_id = lock.get_lock(self.connection, lock_name,
                timeout_seconds=1)
        self.assertIsNotNone(request_id)
        lock.heartbeat(self.connection, lock_name, request_id)
        lock.release_lock(self.connection, lock_name, request_id)

    def test_heartbeat_invalid_request_id(self):
        lock_name = 'foo'

        request_id = lock.get_lock(self.connection, lock_name,
                timeout_seconds=1)
        self.assertIsNotNone(request_id)
        invalid_request_id = 'INVALID_PREFIX_' + request_id
        with self.assertRaises(exceptions.RequestIdMismatch):
            lock.heartbeat(self.connection, lock_name, invalid_request_id)

    def test_heartbeat_expired_lock(self):
        lock_name = 'foo'

        request_id = lock.get_lock(self.connection, lock_name,
                timeout_seconds=1)
        self.assertIsNotNone(request_id)
        time.sleep(2)
        with self.assertRaises(exceptions.NonExistantLock):
            lock.heartbeat(self.connection, lock_name, request_id)

    def test_get_two_locks(self):
        lock_name_a = 'foo'
        lock_name_b = 'bar'

        request_id_a = lock.get_lock(self.connection, lock_name_a,
                timeout_seconds=1)
        self.assertIsNotNone(request_id_a)

        request_id_b = lock.get_lock(self.connection, lock_name_b,
                timeout_seconds=1)
        self.assertIsNotNone(request_id_b)

        lock.release_lock(self.connection, lock_name_a, request_id_a)
        lock.release_lock(self.connection, lock_name_b, request_id_b)


#class ExclusiveLockContentionTest(unittest.TestCase):
#    def setUp(self):
#        self.connection = redis.Redis()
#        self.connection.flushall()


if __name__ == '__main__':
    unittest.main()
