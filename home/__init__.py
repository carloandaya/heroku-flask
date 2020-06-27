import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    if test_config:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    elif os.environ.get('IS_HEROKU') == 'True':
        # load from environment variables
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY'),
        )                
    else:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def hello():
        return f'Hello, World!'

    return app