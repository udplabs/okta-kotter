import json
import logging

from functools import wraps

import requests

from flask import current_app, Response, session, request
from jwcrypto import jwt, jwk
# from werkzeug.exceptions import Unauthorized


JWK_CACHE = []

# TODO: this should probably be a class that can take auth server params as config
def validate_access_token(token, scopes):
    global JWK_CACHE
    if len(JWK_CACHE) == 0:
        url = '{}/v1/keys'.format(current_app.config['OKTA_ISSUER'])
        resp = requests.get(url)
        keys = json.loads(resp.content)['keys']
    else:
        keys = JWK_CACHE
    # TODO: use keyset 'add' since there could be multiple keys: jwk.JWKSet()
    key = jwk.JWK(**keys[0])
    # verify token and check claims
    # NOTE: .verify() is implied by checking the claims with the key
    verified_token = jwt.JWT(key=key, jwt=token)
    claims = json.loads(verified_token.claims)
    # TODO: raise custom error to indicate scopes didn't match, other failures
    for scope in scopes:
        assert scope in claims['scp']
    assert claims['iss'] == current_app.config['OKTA_ISSUER']
    assert claims['cid'] == current_app.config['OKTA_CLIENT_ID']
    assert claims['aud'] == current_app.config['OKTA_AUDIENCE']


def authorize(scopes=[]):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                auth_header = request.headers.get('Authorization')
                type_, token = auth_header.split(' ')
                validate_access_token(token, scopes)
            except Exception as e:
                logging.exception(str(e))
                # raise Unauthorized
                response = {'status': 'UNAUTHORIZED'}
                return Response(json.dumps(response), 401)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
