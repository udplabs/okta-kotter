import os

from flask_dance.consumer import OAuth2ConsumerBlueprint

issuer = os.environ.get('OKTA_ISSUER')
bp_name = 'okta'
conf = {
    'client_id': os.environ.get('OKTA_CLIENT_ID'),
    'client_secret': os.environ.get('OKTA_CLIENT_SECRET'),
    'base_url': issuer,
    'token_url': '{}/v1/token'.format(issuer),
    'authorization_url': '{}/v1/authorize'.format(issuer),
    'scope': os.environ.get('OKTA_SCOPES').split(','),
    'redirect_url': '{}/authorization/redirect?conf=okta'.format(os.environ.get('APP_URL'))
}
okta_blueprint = OAuth2ConsumerBlueprint('okta', __name__, **conf)

conf.update({
    'scope': os.environ.get('OKTA_ADMIN_SCOPES').split(','),
    'redirect_url': '{}/authorization/redirect?conf=okta-admin'.format(os.environ.get('APP_URL'))
})
okta_admin_blueprint = OAuth2ConsumerBlueprint('okta-admin', __name__, **conf)
