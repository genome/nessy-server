from flask.ext.restful import Api
from . import views


api = Api(default_mediatype='application/json')
api.add_resource(views.ClaimListView, '/claims/')
api.add_resource(views.ClaimView, '/claims/<int:claim_id>/')
