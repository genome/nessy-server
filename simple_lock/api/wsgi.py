from . import v1
import flask


app = flask.Flask('Locking Service')
app.register_blueprint(v1.blueprint, prefix='/v1')


if __name__ == '__main__':
    app.run(debug=True)
