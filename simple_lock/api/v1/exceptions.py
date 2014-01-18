class APIException(Exception):
    def __init__(self, **kwargs):
        super(APIException, self).__init__()
        kwargs['exception_class'] = self.__class__.__name__
        self.as_dict = kwargs


class InvalidParameters(APIException):
    status_code = 400
