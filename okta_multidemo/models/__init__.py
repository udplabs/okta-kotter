import os

from flask import g, session, current_app

from .backends.tinydb import Model as TinyDBModel, get_db as get_tinydb
from .backends.dynamodb import Model as DynamoDBModel, get_db as get_dynamodb

TENANT_MODELS = [
    'products',
    'orders',
    'settings',
    'clients',
    'events',
]
ALL_MODELS = TENANT_MODELS.append('tenants')


def get_db(db_path):
    if current_app.config['ENV'] == 'production':
        db = get_dynamodb()
    else:
        db = get_tinydb(db_path)
    return db


def get_model(table):
    # TODO: raise error if table not in TENANT_MODELS
    if current_app.config['ENV'] == 'production':
        model = DynamoDBModel(
            g.db, session.get('subdomain', 'localhost'), table, os.getenv('DB_TABLE_PREFIX'))
    else:
        model = TinyDBModel(g.db, session.get('subdomain', 'localhost'), table)
    return model
