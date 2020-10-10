from flask import g, session, current_app

from .backends.tinydb import TinyDBModel

TENANT_MODELS = [
    'products',
    'orders',
    'settings',
    'clients',
    'events',
]
ALL_MODELS = TENANT_MODELS.append('tenants')


def get_model(table):
    # TODO: raise error if table not in TENANT_MODELS
    if current_app.config['ENV'] == 'production':
        # TODO: DynamoDB
        pass
    else:
        model = TinyDBModel(g.db, session['subdomain'], table)
    return model
