class LockingException(Exception):
    def __init__(self, **kwargs):
        Exception.__init__(self, self.TEMPLATE.format(**kwargs))

class NoRequestId(LockingException):
    TEMPLATE = 'No request_id supplied:  name = "{name}"'

class RequestIdMismatch(LockingException):
    TEMPLATE = 'Mismatched request_id ({request_id}) supplied for '\
            'lock resource "{name}".'

class NonExistantLock(LockingException):
    TEMPLATE = 'Lock ({name}) does not exist'

class UnknownError(LockingException):
    TEMPLATE = 'Unknown error code ({code}): '\
            'name = "{name}", request_id = {request_id}'


_STORAGE_CODE_MAP = {
    -1: RequestIdMismatch,
    -2: NonExistantLock,
}
def raise_storage_exception(code, name, request_id):
    if code != 0:
        cls = _STORAGE_CODE_MAP.get(code, UnknownError)
        raise cls(code=code, name=name, request_id=request_id)
