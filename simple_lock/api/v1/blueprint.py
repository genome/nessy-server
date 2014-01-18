from . import claim
import flask


claim_view = claim.ClaimView.as_view('claim_api')
blueprint = flask.Blueprint('blueprint', 'v1')

blueprint.add_url_rule('/claims/', defaults={'claim_id': None},
        view_func=claim_view, methods=['GET'])
blueprint.add_url_rule('/claims/',
        view_func=claim_view, methods=['POST'])
blueprint.add_url_rule('/claims/<int:claim_id>/',
        view_func=claim_view, methods=['GET', 'PATCH', 'PUT'])
