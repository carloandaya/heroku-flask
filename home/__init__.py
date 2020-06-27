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
            MONGO_URI=os.environ.get('MONGO_URI'),
        )                
    else:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    
    # a simple page that says hello
    @app.route('/')
    def hello():
        mongo_db = db.get_db()
        camera = mongo_db.cameras.find_one()   
        print(type(camera))
        return 'Hello, World! I have a {make} {model}.'.format(**camera)

    return app