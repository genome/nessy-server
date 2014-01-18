from . import claim
from . import exceptions

import flask


__all__ = ['blueprint']


blueprint = flask.Blueprint('blueprint', 'v1')


@blueprint.errorhandler(exceptions.APIException)
def _api_exception_handler(exc):
    response = flask.jsonify(exc.as_dict)
    response.status_code = exc.status_code
    return response


claim_view = claim.ClaimView.as_view('claim_api')
blueprint.add_url_rule('/claims/', defaults={'claim_id': None},
        view_func=claim_view, methods=['GET'])
blueprint.add_url_rule('/claims/',
        view_func=claim_view, methods=['POST'])
blueprint.add_url_rule('/claims/<int:claim_id>/',
        view_func=claim_view, methods=['GET', 'PATCH', 'PUT'])
