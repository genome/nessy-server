import redis
import time
import unittest

from libs import lock
from libs.lock import exceptions

class LockDataTest(unittest.TestCase):
    def setUp(self):
        self.connection = redis.Redis()
        self.connection.flushall()

    def test_request_sets_owner_data(self):
        lock_name = 'foo'
        data = {
            'bar': 'baz'
        }

        result = lock.request_lock(self.connection, lock_name,
                timeout_seconds=1, data=data)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.request_id)
        self.assertEqual(result.request_id, result.owner_id)
        self.assertEqual(result.owner_data, data)

    def test_request_returns_owner_data(self):
        lock_name = 'foo'
        data = {
            'bar': 'baz'
        }

        result = lock.request_lock(
                self.connection, lock_name, timeout_seconds=1, data=data)
        self.assertTrue(result.success)

        new_result = lock.request_lock(
                self.connection, lock_name, timeout_seconds=1)
        self.assertFalse(new_result.success)
        self.assertEqual(result.request_id, new_result.owner_id)
        self.assertEqual(data, new_result.owner_data)


class ExclusiveLockNoContentionTest(unittest.TestCase):
    def setUp(self):
        self.connection = redis.Redis()
        self.connection.flushall()

    def test_request_released_lock(self):
        lock_name = 'foo'

        result = lock.request_lock(self.connection, lock_name,
                timeout_seconds=1)
        self.assertTrue(result.success)
        lock.release_lock(self.connection, lock_name, result.request_id)

        new_result = lock.request_lock(self.connection, lock_name,
                timeout_seconds=1)
        self.assertTrue(new_result.success)
        self.assertNotEqual(result.request_id, new_result.request_id)
        lock.release_lock(self.connection, lock_name, new_result.request_id)

    def test_release_invalid_request_id(self):
        lock_name = 'foo'

        result = lock.request_lock(self.connection, lock_name,
                timeout_seconds=1)
        self.assertTrue(result.success)

        invalid_request_id = 'INVALID_PREFIX_' + result.request_id
        with self.assertRaises(exceptions.RequestIdMismatch):
            lock.release_lock(self.connection, lock_name, invalid_request_id)

    def test_release_expired_lock(self):
        lock_name = 'foo'

        result = lock.request_lock(self.connection, lock_name,
                timeout_milliseconds=10)
        self.assertTrue(result.success)

        time.sleep(0.020)

        with self.assertRaises(exceptions.NonExistantLock):
            lock.release_lock(self.connection, lock_name, result.request_id)

    def test_heartbeat_extends_ttl(self):
        lock_name = 'foo'

        result = lock.request_lock(self.connection, lock_name,
                timeout_milliseconds=30)
        self.assertTrue(result.success)
        time.sleep(0.020)

        lock.heartbeat(self.connection, lock_name, result.request_id)
        time.sleep(0.020)
        lock.release_lock(self.connection, lock_name, result.request_id)


    def test_request_expired_lock(self):
        lock_name = 'foo'

        result = lock.request_lock(self.connection, lock_name,
                timeout_milliseconds=10)
        self.assertTrue(result.success)

        time.sleep(0.020)
        new_result = lock.request_lock(self.connection, lock_name,
                timeout_seconds=1)
        self.assertTrue(new_result.success)
        self.assertNotEqual(result.request_id, new_result.request_id)

    def test_heartbeat_valid_lock(self):
        lock_name = 'foo'

        result = lock.request_lock(self.connection, lock_name,
                timeout_seconds=1)
        self.assertTrue(result.success)
        lock.heartbeat(self.connection, lock_name, result.request_id)

    def test_heartbeat_invalid_request_id(self):
        lock_name = 'foo'

        result = lock.request_lock(self.connection, lock_name,
                timeout_seconds=1)
        self.assertTrue(result.success)

        invalid_request_id = 'INVALID_PREFIX_' + result.request_id
        with self.assertRaises(exceptions.RequestIdMismatch):
            lock.heartbeat(self.connection, lock_name, invalid_request_id)

    def test_heartbeat_expired_lock(self):
        lock_name = 'foo'

        result = lock.request_lock(self.connection, lock_name,
                timeout_milliseconds=10)
        self.assertTrue(result.success)
        time.sleep(0.020)
        with self.assertRaises(exceptions.NonExistantLock):
            lock.heartbeat(self.connection, lock_name, result.request_id)

    def test_request_two_locks(self):
        lock_name_a = 'foo'
        lock_name_b = 'bar'

        result_a = lock.request_lock(self.connection, lock_name_a,
                timeout_seconds=1)
        self.assertTrue(result_a.success)

        result_b = lock.request_lock(self.connection, lock_name_b,
                timeout_seconds=1)
        self.assertTrue(result_b.success)

        lock.release_lock(self.connection, lock_name_a, result_a.request_id)
        lock.release_lock(self.connection, lock_name_b, result_b.request_id)


if __name__ == '__main__':
    unittest.main()
