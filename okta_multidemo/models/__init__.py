import os

from flask import g, session, current_app

from .backends.tinydb import Model as TinyDBModel, get_db as get_tinydb
from .backends.dynamodb import Model as DynamoDBModel, get_db as get_dynamodb

TENANT_MODELS = [
    'products',
    'orders',
    'clients',
    'events',
]
ALL_MODELS = TENANT_MODELS.append('tenants')


def get_db():
    db = getattr(g, 'db', None)
    if not db:
        print('hit here?')
        # if current_app.config['ENV'] == 'production':
        db = g.db = get_dynamodb()
        # else:
        #     db = g.db = get_tinydb(current_app.config['DB_PATH'])
    return db


def get_model(table, subdomain=None):
    # TODO: raise error if table not in TENANT_MODELS
    db = get_db()
    if not subdomain:
        subdomain = session.get('subdomain', 'localhost')
    # if current_app.config['ENV'] == 'production':
    model = DynamoDBModel(
        db, subdomain, table, os.getenv('DB_TABLE_PREFIX'))
    # else:
    #     model = TinyDBModel(db, subdomain, table)
    return model
