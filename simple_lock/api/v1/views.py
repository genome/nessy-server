from . import request_parsers
from flask import g
from flask.ext.restful import Resource


__all__ = ['ClaimListView', 'ClaimView']


class ClaimListView(Resource):
    def get(self):
        pass

    def post(self):
        data, errors = request_parsers.get_claim_post_data()
        if errors:
            return errors, 400
        return '', 201, {'Location': '/v1/claims/42/'}


class ClaimView(Resource):
    def get(self, claim_id):
        return {'hi': 'there'}

    def patch(self, claim_id):
        data, errors = request_parsers.get_claim_update_data()
        if errors:
            return errors, 400
        return '', 200

    def put(self, claim_id):
        return self.patch(claim_id)
