from . import application

app = application.create_app('sqlite:///db.sqlite')


if __name__ == '__main__':
    app.run(debug=True)
