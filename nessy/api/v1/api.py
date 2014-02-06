from flask.ext.restful import Api
from . import views


api = Api(default_mediatype='application/json')
api.add_resource(views.ClaimListView, '/claims/', endpoint='claim-list')
api.add_resource(views.ClaimView, '/claims/<int:id>/', endpoint='claim')
