from . import exceptions
from flask.ext.restful import reqparse
import simplejson


__all__ = []

def pass_through_type(value):
    return value


_claim_post = reqparse.RequestParser()
_claim_post.add_argument('resource', type=str)
_claim_post.add_argument('timeout', type=float)
_claim_post.add_argument('user_data', type=pass_through_type)
def get_claim_post_data():
    data = _claim_post.parse_args()

    errors = {}

    if data['resource'] is None or data['resource'] == '':
        errors['resource'] = 'No resource specified'
    if data['timeout'] is None:
        errors['timeout'] = 'No timeout specified'
    elif data['timeout'] < 0:
        errors['timeout'] = 'Positive timeout required (in seconds)'

    try:
        data['user_data'] = simplejson.dumps(data['user_data'])
    except TypeError, ValueError:
        errors['user_data'] = 'Failed to serialize user_data'

    return data, errors


_claim_update = reqparse.RequestParser()
_claim_update.add_argument('timeout', type=float)
_claim_update.add_argument('status', type=str)
def get_claim_update_data():
    data = _claim_update.parse_args()

    errors = {}

    if data['status'] is not None:
        if data['status'] not in ['active', 'released', 'revoked']:
            errors['status'] = 'Invalid value for status'
    if data['timeout'] is not None and data['timeout'] < 0:
        errors['timeout'] = 'Positive timeout required (in seconds)'

    return data, errors


_claim_list = reqparse.RequestParser()
_claim_list.add_argument('limit', type=int, location='args', default=10)
_claim_list.add_argument('offset', type=int, location='args', default=0)
_claim_list.add_argument('resource', type=str, location='args')
_claim_list.add_argument('status', type=str, location='args')
def get_claim_list_data():
    data = _claim_list.parse_args()
    return data, {}
