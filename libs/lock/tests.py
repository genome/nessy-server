import redis
import time
import unittest

from libs import lock
from libs.lock import exceptions


class ExclusiveLockNoContentionTest(unittest.TestCase):
    def setUp(self):
        self.connection = redis.Redis()
        self.connection.flushall()

    def test_get_sets_owner_data(self):
        lock_name = 'foo'
        data = {
            'bar': 'baz'
        }

        (success, request_id, owner_id, owner_data) = lock.request_lock(
                self.connection, lock_name, timeout_seconds=1, data=data)
        self.assertTrue(success)
        self.assertIsNotNone(request_id)
        self.assertEqual(request_id, owner_id)
        self.assertEqual(owner_data, data)

    def test_get_released_lock(self):
        lock_name = 'foo'

        success, request_id, _, _ = lock.request_lock(
                self.connection, lock_name, timeout_seconds=1)
        self.assertTrue(success)
        lock.release_lock(self.connection, lock_name, request_id)

        new_success, new_request_id, _, _ = lock.request_lock(
                self.connection, lock_name, timeout_seconds=1)
        self.assertTrue(new_success)
        self.assertNotEqual(request_id, new_request_id)
        lock.release_lock(self.connection, lock_name, new_request_id)

    def test_release_invalid_request_id(self):
        lock_name = 'foo'

        success, request_id, _, _ = lock.request_lock(
                self.connection, lock_name, timeout_seconds=1)
        self.assertTrue(success)

        invalid_request_id = 'INVALID_PREFIX_' + request_id
        with self.assertRaises(exceptions.RequestIdMismatch):
            lock.release_lock(self.connection, lock_name, invalid_request_id)

    def test_release_expired_lock(self):
        lock_name = 'foo'

        success, request_id, _, _ = lock.request_lock(
                self.connection, lock_name, timeout_milliseconds=10)
        self.assertTrue(success)

        time.sleep(0.020)

        with self.assertRaises(exceptions.NonExistantLock):
            lock.release_lock(self.connection, lock_name, request_id)

    def test_heartbeat_extends_ttl(self):
        lock_name = 'foo'

        success, request_id, _, _ = lock.request_lock(
                self.connection, lock_name, timeout_milliseconds=30)
        self.assertTrue(success)
        time.sleep(0.020)

        lock.heartbeat(self.connection, lock_name, request_id)
        time.sleep(0.020)
        lock.release_lock(self.connection, lock_name, request_id)


    def test_get_expired_lock(self):
        lock_name = 'foo'

        success, request_id, _, _ = lock.request_lock(
                self.connection, lock_name, timeout_milliseconds=10)
        self.assertTrue(success)

        time.sleep(0.020)
        new_success, new_request_id, _, _ = lock.request_lock(
                self.connection, lock_name, timeout_seconds=1)
        self.assertTrue(new_success)
        self.assertNotEqual(request_id, new_request_id)

    def test_heartbeat_valid_lock(self):
        lock_name = 'foo'

        success, request_id, _, _ = lock.request_lock(
                self.connection, lock_name, timeout_seconds=1)
        self.assertTrue(success)
        lock.heartbeat(self.connection, lock_name, request_id)

    def test_heartbeat_invalid_request_id(self):
        lock_name = 'foo'

        success, request_id, _, _ = lock.request_lock(self.connection, lock_name,
                timeout_seconds=1)
        self.assertTrue(success)
        invalid_request_id = 'INVALID_PREFIX_' + request_id
        with self.assertRaises(exceptions.RequestIdMismatch):
            lock.heartbeat(self.connection, lock_name, invalid_request_id)

    def test_heartbeat_expired_lock(self):
        lock_name = 'foo'

        success, request_id, _, _ = lock.request_lock(
                self.connection, lock_name, timeout_milliseconds=10)
        self.assertTrue(success)
        time.sleep(0.020)
        with self.assertRaises(exceptions.NonExistantLock):
            lock.heartbeat(self.connection, lock_name, request_id)

    def test_get_two_locks(self):
        lock_name_a = 'foo'
        lock_name_b = 'bar'

        suc_a, request_id_a, _, _ = lock.request_lock(self.connection, lock_name_a,
                timeout_seconds=1)
        self.assertTrue(suc_a)

        suc_b, request_id_b, _, _ = lock.request_lock(self.connection, lock_name_b,
                timeout_seconds=1)
        self.assertTrue(suc_b)

        lock.release_lock(self.connection, lock_name_a, request_id_a)
        lock.release_lock(self.connection, lock_name_b, request_id_b)


class ExclusiveLockContentionTest(unittest.TestCase):
    def setUp(self):
        self.connection = redis.Redis()
        self.connection.flushall()

    def test_get_returns_owner_data(self):
        lock_name = 'foo'
        data = {
            'bar': 'baz'
        }

        (success, original_request_id, _, _) = lock.request_lock(
                self.connection, lock_name, timeout_seconds=1, data=data)
        self.assertTrue(success)

        (new_success, request_id, owner_id, owner_data) = lock.request_lock(
                self.connection, lock_name, timeout_seconds=1)
        self.assertFalse(new_success)
        self.assertEqual(original_request_id, owner_id)
        self.assertEqual(data, owner_data)


if __name__ == '__main__':
    unittest.main()
