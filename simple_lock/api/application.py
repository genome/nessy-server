from . import v1
from .. import backend
import flask


__all__ = ['create_app']


def create_app(database_string):
    factory = _create_factory(database_string)
    app = _create_app_from_blueprints()

    _attach_factory_to_app(factory, app)

    return app


def _create_factory(database_string):
    factory = backend.ActorFactory(database_string)
    factory.create_tables()

    return factory

def _create_app_from_blueprints():
    app = flask.Flask('Locking Service')
    app.register_blueprint(v1.blueprint, url_prefix='/v1')

    return app

def _attach_factory_to_app(factory, app):
    @app.before_request
    def before_request():
        flask.g.actor = factory.create_actor()

    @app.teardown_request
    def teardown_request(exception):
        flask.g.actor.close()
