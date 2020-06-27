from pymongo import MongoClient

from flask import current_app, g

def get_db(): 
    if 'db' not in g:         
        client = MongoClient(current_app.config['MONGO_URI'])
        g.db = client.home
    return g.db 

