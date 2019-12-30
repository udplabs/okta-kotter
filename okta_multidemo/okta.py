import os

from flask_dance.consumer import OAuth2ConsumerBlueprint

# TODO: use Flask app env instead of os.environ
issuer = os.environ.get('OKTA_ISSUER')
okta_blueprint = OAuth2ConsumerBlueprint(
    'okta', __name__,
    client_id=os.environ.get('OKTA_CLIENT_ID'),
    client_secret=os.environ.get('OKTA_CLIENT_SECRET'),
    base_url=issuer,
    token_url='{}/v1/token'.format(issuer),
    authorization_url='{}/v1/authorize'.format(issuer),
    scope=os.environ.get('OKTA_SCOPES').split(',')
    # redirect_url='http://localhost:5000/other',
)
