import hashlib
import redis


class Script(object):
    def __init__(self, script_body):
        self.script_body = script_body
        self.script_hash = hashlib.sha1(script_body).hexdigest()

    def __call__(self, connection=None, keys=[], args=[]):
        if connection is None:
            raise TypeError("You must specify a connection")

        num_keys = len(keys)
        keys_and_args = keys + args
        try:
            return connection.evalsha(self.script_hash,
                    num_keys, *keys_and_args)
        except redis.exceptions.ResponseError:
            return connection.eval(self.script_body, num_keys, *keys_and_args)
