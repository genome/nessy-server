from rest_framework.exceptions import APIException


class LockContention(APIException):
    status_code = 409
    detail = 'Lock is in contention.  Try again later.'
