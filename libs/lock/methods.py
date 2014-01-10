from libs.lock import exceptions
from libs.lock import lua
from libs.lock.script import Script

import simplejson

__all__ = [
    'heartbeat',
    'release_lock',
    'request_lock',
    'retry_request',
]


class RequestResult(object):
    def __init__(self, lock_name, success, request_id, owner_id, owner_data):
        self.lock_name = lock_name
        self.success = success
        self.request_id = request_id
        self.owner_id = owner_id
        self.owner_data = owner_data

_request_lock_script = Script(lua.load('queue', 'request_lock'))
def request_lock(connection, name, timeout_seconds=None,
        timeout_milliseconds=None, data=None):
    timeout_type, timeout = _get_timeout(timeout_seconds, timeout_milliseconds)
    success, request_id, owner_id, owner_data = _request_lock_script(connection,
                    keys=['last_request_id', name] + _queue_keys(name),
                    args=[timeout, timeout_type, simplejson.dumps(data)])

    return RequestResult(name, success, str(request_id),
            str(owner_id), simplejson.loads(owner_data))

_retry_lock_script = Script(lua.load('queue', 'retry_lock'))
def retry_request(connection, name, request_id):
    success, owner_id, owner_data = _retry_lock_script(connection,
            keys=[name] + _queue_keys(name),
            args=[request_id])
    return RequestResult(name, success, request_id,
            str(owner_id), simplejson.dumps(owner_data))

_heartbeat_script = Script(lua.load('heartbeat'))
def heartbeat(connection, name, request_id):
    if request_id is None:
        raise exceptions.NoRequestId(name)

    code, message = _heartbeat_script(connection,
            keys=[name], args=[request_id])

    exceptions.raise_storage_exception(code, name, request_id)
    return

_release_lock_script = Script(lua.load('release_lock'))
def release_lock(connection, name, request_id):
    if request_id is None:
        raise exceptions.NoRequestId(name)

    code, message = _release_lock_script(connection,
            keys=[name], args=[request_id])

    exceptions.raise_storage_exception(code, name, request_id)
    return


def _get_timeout(timeout_seconds, timeout_milliseconds):
    if timeout_seconds is not None and timeout_milliseconds is not None:
        raise exceptions.MultipleTimeouts(timeout_seconds=timeout_seconds,
                timeout_milliseconds=timeout_milliseconds)
    elif timeout_seconds is None and timeout_milliseconds is None:
        raise exceptions.NoTimeout(name)

    if timeout_milliseconds is not None:
        return 'PEXPIRE', timeout_milliseconds
    else:
        return 'EXPIRE', timeout_seconds

def _queue_keys(name):
    return ['%s/%s' % (name, k) for k in
                ['queue', 'queue_timeout_type', 'queue_timeout', 'queue_data']
    ]
