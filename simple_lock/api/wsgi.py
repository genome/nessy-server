from . import application
import os

app = application.create_app(os.environ['LOCKING_DB'])


if __name__ == '__main__':
    app.run(debug=True)
