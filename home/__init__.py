import os

from flask import Flask, request, redirect, session, url_for


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
            CLIENT_ID=os.environ.get('CLIENT_ID'),
            CLIENT_SECRET=os.environ.get('CLIENT_SECRET'),
            AUTHORIZATION_BASE_URL=os.environ.get('AUTHORIZATION_BASE_URL'),
            TOKEN_URL=os.environ.get('TOKEN_URL'),
            SCOPE=os.environ.get('SCOPE'),
            REDIRECT_URI=os.environ.get('REDIRECT_URI'),
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
    
    db.init_app(app)

    with app.app_context(): 
        from . import auth
        app.register_blueprint(auth.bp)
        app.add_url_rule('/', endpoint='hello')

    return app