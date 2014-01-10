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


def heartbeat(connection, name, secret):
    if secret is None:
        raise RuntimeError('Must supply a secret')

    actual_secret = connection.get(name)
    if actual_secret == secret:
        ttl = connection.get(_timeout_key(name))
        connection.expire(name, ttl)
        connection.expire(_timeout_key(name), ttl)

    else:
        raise RuntimeError(
                'Incorrect (%s) secret supplied for lock resource "%s".'
                % (secret, name))


def release_lock(connection, name, secret):
    if secret is None:
        raise RuntimeError('Must supply a secret')

    actual_secret = connection.get(name)
    if actual_secret == secret:
        connection.delete(_timeout_key(name))
        connection.delete(name)

    else:
        raise RuntimeError(
                'Incorrect (%s) secret supplied for lock resource "%s".'
                % (secret, name))


def _timeout_key(name):
    return name + '/timeout'
