import functools
import uuid

from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask.json import jsonify

from requests_oauthlib import OAuth2Session
from home.db import get_db

bp = Blueprint('auth', __name__)

authorization_base_url = current_app.config.get('AUTHORIZATION_BASE_URL')
token_url = current_app.config.get('TOKEN_URL')
scope = current_app.config.get('SCOPE')
redirect_uri = current_app.config.get('REDIRECT_URI')
client_id = current_app.config.get('CLIENT_ID')
client_secret = current_app.config.get('CLIENT_SECRET')


# a simple page that says hello
@bp.route('/')
def hello():
    mongo_db = get_db()
    camera = mongo_db.home.cameras.find_one()           
    return 'Hello, World! I have a {make} {model}.'.format(**camera)

@bp.route('/login')
def login():
    session['oauth_state'] = str(uuid.uuid4()) 
    msgraph = OAuth2Session(client_id, scope=scope, state=session['oauth_state'], redirect_uri=redirect_uri)
    authorization_url, _ = msgraph.authorization_url(authorization_base_url)

    return redirect(authorization_url)

@bp.route('/login/authorized')
def authorized():
    # Verify the state value that was passed in the request
    if str(session['oauth_state']) != str(request.args['state']): 
        raise Exception('State returned to redirect URL does not match!')

    msgraph = OAuth2Session(client_id, state=session['oauth_state'], redirect_uri=redirect_uri)
    token = msgraph.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)    
    session['oauth_token'] = token

    return 'You are authorized!'


@bp.route('/profile')
def profile(): 
    msgraph = OAuth2Session(client_id, token=session['oauth_token'])
    user_data = msgraph.get('https://graph.microsoft.com/v1.0/me')
    return jsonify(user_data.json())