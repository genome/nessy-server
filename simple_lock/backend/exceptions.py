class BackendException(Exception):
    def __init__(self, **kwargs):
        super(BackendException, self).__init__()
        kwargs['exception_class'] = self.__class__.__name__
        self.as_dict = kwargs

class ClaimNotFound(BackendException):
    pass
