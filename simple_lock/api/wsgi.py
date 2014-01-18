from . import application

app = application.create_app('sqlite:///:memory:')


if __name__ == '__main__':
    app.run(debug=True)
