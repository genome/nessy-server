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
        raise exceptions.NoRequestId(name)

    code, message = _heartbeat_script(connection,
            keys=[name, _timeout_key(name)],
            args=[request_id])

    exceptions.raise_storage_exception(code, name, request_id)
    return


_release_lock_script = Script(lua.load('release_lock'))
def release_lock(connection, name, request_id):
    if request_id is None:
        raise exceptions.NoRequestId(name)

    code, message = _release_lock_script(connection,
            keys=[name, _timeout_key(name)],
            args=[request_id])

    exceptions.raise_storage_exception(code, name, request_id)
    return


def _timeout_key(name):
    return name + '/timeout'
