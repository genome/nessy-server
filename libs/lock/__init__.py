from libs.lock import lua
from libs.lock.script import Script


_get_lock_script = Script(lua.load('get_lock'))
def get_lock(connection, name, exclusive=True, timeout=600):
    secret, message = _get_lock_script(connection,
            keys=['last_lock_num', name, _timeout_key(name)],
            args=[timeout])
    if secret > 0:
        return str(secret)
    else:
        return


_heartbeat_script = Script(lua.load('heartbeat'))
def heartbeat(connection, name, secret):
    if secret is None:
        raise RuntimeError('Must supply a secret')

    code, message = _heartbeat_script(connection,
            keys=[name, _timeout_key(name)],
            args=[secret])

    if code == 0:
        return
    elif code == -1:
        raise RuntimeError(
                'Incorrect (%s) secret supplied for lock resource "%s".'
                % (secret, name))
    elif code == -2:
        raise RuntimeError('Lock (%s) does not exist' % name)
    elif code == -3:
        raise RuntimeError('CRITICAL: timeout key inaccessible for lock (%s)'
                % name)
    else:
        raise RuntimeError('Unknown error code (%s)' % code)


_release_lock_script = Script(lua.load('release_lock'))
def release_lock(connection, name, secret):
    if secret is None:
        raise RuntimeError('Must supply a secret')

    code, message = _release_lock_script(connection,
            keys=[name, _timeout_key(name)],
            args=[secret])
    if code == 0:
        return
    elif code == -1:
        raise RuntimeError(
                'Incorrect (%s) secret supplied for lock resource "%s".'
                % (secret, name))
    elif code == -2:
        raise RuntimeError('Lock (%s) does not exist' % name)
    else:
        raise RuntimeError('Unknown error code (%s)' % code)


def _timeout_key(name):
    return name + '/timeout'
