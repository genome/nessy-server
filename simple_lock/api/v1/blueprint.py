from . import exceptions
from .api import api
import flask


__all__ = ['blueprint']


blueprint = flask.Blueprint('blueprint', 'v1')


@blueprint.errorhandler(exceptions.APIException)
def _api_exception_handler(exc):
    response = flask.jsonify(exc.as_dict)
    response.status_code = exc.status_code
    return response


api.init_app(blueprint)
