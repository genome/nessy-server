from . import request_parsers
from .output_fields import claim_fields
from flask import g, url_for
from flask.ext.restful import Resource, marshal


__all__ = ['ClaimListView', 'ClaimView']


class ClaimListView(Resource):
    def get(self):
        data, errors = request_parsers.get_claim_list_data()
        if errors:
            return errors, 400

        result = g.actor.list_claims(**data)
        return marshal(result, claim_fields)

    def post(self):
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
        claim = g.actor.get_claim(id)
        if claim:
            return marshal(claim, claim_fields)
        else:
            return {'message': 'No claim found'}, 404

    def patch(self, id):
        data, errors = request_parsers.get_claim_update_data()
        if errors:
            return errors, 400
        try:
            content = g.actor.update_claim(id, **data)
            if content is None:
                return None, 204
            else:
                return marshal(content, claim_fields), 200

        except Exception as e:
            raise e

    def put(self, id):
        return self.patch(id)
