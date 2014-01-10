from libs.lock import exceptions
from libs.lock import lua
from libs.lock.script import Script

__all__ = ['get_lock', 'heartbeat', 'release_lock']


_get_lock_script = Script(lua.load('get_lock'))
def get_lock(connection, name, exclusive=True, timeout=600):
    request_id, message = _get_lock_script(connection,
            keys=['last_request_id', name, _timeout_key(name)],
            args=[timeout])
    if request_id > 0:
        return str(request_id)
    else:
        return


_heartbeat_script = Script(lua.load('heartbeat'))
def heartbeat(connection, name, request_id):
    if request_id is None:
        raise RuntimeError('Must supply a request_id')

    code, message = _heartbeat_script(connection,
            keys=[name, _timeout_key(name)],
            args=[request_id])

    if code == 0:
        return
    elif code == -1:
        raise exceptions.RequestIdMismatch(name, request_id)
    elif code == -2:
        raise RuntimeError('Lock (%s) does not exist' % name)
    else:
        raise RuntimeError('Unknown error code (%s): %s' % (code, message))


_release_lock_script = Script(lua.load('release_lock'))
def release_lock(connection, name, request_id):
    if request_id is None:
        raise RuntimeError('Must supply a request_id')

    code, message = _release_lock_script(connection,
            keys=[name, _timeout_key(name)],
            args=[request_id])
    if code == 0:
        return
    elif code == -1:
        raise exceptions.RequestIdMismatch(name, request_id)
    elif code == -2:
        raise RuntimeError('Lock (%s) does not exist' % name)
    else:
        raise RuntimeError('Unknown error code (%s): %s' % (code, message))


def _timeout_key(name):
    return name + '/timeout'
