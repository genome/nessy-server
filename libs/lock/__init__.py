def get_lock(connection, name, exclusive=True, timeout=600):
    secret = str(connection.incr('last_lock_num'))
    success = connection.set(name, secret, nx=True, ex=timeout)
    if success:
        connection.set(_timeout_key(name), timeout, ex=timeout)
        return secret

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
