import os

from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify

from requests_oauthlib import OAuth2Session



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
        return 'Hello, World! I have a {make} {model}.'.format(**camera)

    authorization_base_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
    token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    scope = ['User.Read', 'Directory.Read.All']
    redirect_uri = 'http://localhost:5000/login/authorized'     # Should match Site URL
    client_id = app.config.get('CLIENT_ID')
    client_secret = app.config.get('CLIENT_SECRET')


    @app.route('/login')
    def login(): 
        msgraph = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
        authorization_url, state = msgraph.authorization_url(authorization_base_url)

        session['oauth_state'] = state
        return redirect(authorization_url)


    @app.route('/login/authorized')
    def authorized():
        msgraph = OAuth2Session(client_id, state=session['oauth_state'], redirect_uri=redirect_uri)
        token = msgraph.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)
        session['oauth_token'] = token
        return 'You are authorized!'


    @app.route('/profile')
    def profile(): 
        msgraph = OAuth2Session(client_id, token=session['oauth_token'])
        user_data = msgraph.get('https://graph.microsoft.com/v1.0/me')
        return jsonify(user_data.json())


    return app