from . import request_parsers
from flask import g
from flask.ext.restful import Resource, fields, marshal_with


__all__ = ['ClaimListView', 'ClaimView']


status_history_fields = {
    'status': fields.String,
    'timestamp': fields.DateTime,
}

claim_fields = {
#    'url': fields.Url(,
    'status': fields.String,
    'status_history': fields.Nested(status_history_fields),
#    'ttl': fields.Float,
}

class ClaimListView(Resource):
    @marshal_with(claim_fields)
    def get(self):
        data, errors = request_parsers.get_claim_list_data()
        if errors:
            return errors, 400

        result = g.actor.list_claims(**data)
        return result

    @marshal_with(claim_fields)
    def post(self):
        data, errors = request_parsers.get_claim_post_data()
        if errors:
            return errors, 400

        claim, ownership = g.actor.create_claim(**data)
        if ownership:
            status_code = 201
        else:
            status_code = 202
        return claim, status_code, {'Location': '/v1/claims/%d/' % claim.id}


class ClaimView(Resource):
    @marshal_with(claim_fields)
    def get(self, claim_id):
        claim = g.actor.get_claim(claim_id)
        if claim:
            return claim
        else:
            return {'message': 'No claim found'}, 404

    def patch(self, claim_id):
        data, errors = request_parsers.get_claim_update_data()
        if errors:
            return errors, 400
        return '', 200

    def put(self, claim_id):
        return self.patch(claim_id)
