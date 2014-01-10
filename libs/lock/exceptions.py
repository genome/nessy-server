class LockingException(Exception):
    def __init__(self, name, request_id):
        Exception.__init__(self, self.TEMPLATE.format(
            name=name, request_id=request_id))
        self.name = name
        self.request_id = request_id

class RequestIdMismatch(LockingException):
    TEMPLATE = 'Mismatched request_id ({request_id}) supplied for '\
            'lock resource "{name}".'
