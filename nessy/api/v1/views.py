from . import request_parsers
from .output_fields import claim_fields
from contextlib import contextmanager
from flask import g, request, url_for
from flask.ext.restful import Resource, marshal
from nessy.backend import exceptions
import os

__all__ = ['ClaimListView', 'ClaimView']


@contextmanager
def timer(label):
    # NOTE: We load the statsd module lazily, because it binds configuration
    # globally, which isn't safe when running with uWSGI in prefork mode.
    import statsd
    statsd.Connection.set_defaults(
            host=os.environ.get('LOCKING_STATSD_HOST', 'localhost'),
            port=os.environ.get('LOCKING_STATSD_PORT', 8125))
    timer = statsd.Timer('nessy-server')
    with timer.time(label):
        yield


class ClaimListView(Resource):
    def get(self):
        with timer('list-get'):
            request.data  # read entire request body (avoid uWSGI issues)
            data, errors = request_parsers.get_claim_list_data()
            if errors:
                return errors, 400

            result = g.actor.list_claims(**data)
            return marshal(result, claim_fields)

    def post(self):
        with timer('list-post'):
            request.data  # read entire request body (avoid uWSGI issues)
            data, errors = request_parsers.get_claim_post_data()
            if errors:
                return errors, 400

            claim, ownership = g.actor.create_claim(**data)
            if ownership:
                status_code = 201
            else:
                status_code = 202
            return (marshal(claim, claim_fields), status_code,
                    {'Location': _construct_claim_url(claim.id)})

def _construct_claim_url(claim_id):
    return url_for('claim', id=claim_id)


class ClaimView(Resource):
    def get(self, id):
        with timer('detail-get'):
            request.data  # read entire request body (avoid uWSGI issues)
            claim = g.actor.get_claim(id)
            if claim:
                return marshal(claim, claim_fields)
            else:
                return {'message': 'No claim found'}, 404

    def patch(self, id):
        with timer('detail-patch'):
            request.data  # read entire request body (avoid uWSGI issues)
            data, errors = request_parsers.get_claim_update_data()
            if errors:
                return errors, 400

            try:
                content = g.actor.update_claim(id, **data)
                if _should_return_204(content, data):
                    return None, 204
                else:
                    return marshal(content, claim_fields), 200

            except exceptions.InvalidRequest as e:
                return e.as_dict, 400
            except exceptions.ClaimNotFound as e:
                return e.as_dict, 404
            except exceptions.ConflictException as e:
                return e.as_dict, 409

            except exceptions.DatabaseError as e:
                return e.as_dict, 503
            except exceptions.UnexpectedError as e:
                return e.as_dict, 500


_204_STATUSES = {
    'aborted',
    'released',
    'revoked',
    'withdrawn',
}
def _should_return_204(content, data):
    if 'status' in data:
        if data['status'] in _204_STATUSES:
            return True
    return False
