import json
import logging
import time

from functools import wraps

import requests

from flask import current_app, Response, session, request
from jwcrypto import jwt, jwk

from ..util import OktaAPIClient, UserFactorResource

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
    # assert claims['cid'] == current_app.config['OKTA_CLIENT_ID']
    # TODO: ^^^ keep whitelist of approved clients?
    assert claims['aud'] == current_app.config['OKTA_AUDIENCE']
    return claims


def authorize(scopes=[]):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                auth_header = request.headers.get('Authorization')
                type_, token = auth_header.split(' ')
                claims = validate_access_token(token, scopes)
            except Exception as e:
                logging.exception(str(e))
                # raise Unauthorized
                response = {'status': 'UNAUTHORIZED'}
                return Response(json.dumps(response), 401)
            kwargs.update({'claims': claims})
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def mfa():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id', None)
            if not user_id:  # must be client credentials; no MFA
                return f(*args, **kwargs)
            okta = OktaAPIClient(
                current_app.config['OKTA_BASE_URL'],
                current_app.config['OKTA_API_KEY']
            )
            okta.api.add_resource(
                resource_name='factors',
                resource_class=UserFactorResource
            )
            # get factors available for this user -- for now, just grab
            #   the first one; which factor to use could be part of the
            #   user's profile admin in the app
            factors = okta.api.factors.get(user_id)
            factor = [i for i in factors.body if i['status'] == 'ACTIVE'][0]
            factor_id = factor['id']
            challenge = okta.api.factors.issue(user_id, factor_id)
            poll_link = challenge.body['_links']['poll']['href']
            transaction_id = poll_link.split('/')[-1]  # not sure why tx ID is not included in payload
            status = challenge.body['factorResult']
            wait_ct = 0
            while status == 'WAITING':
                time.sleep(2)
                verify = okta.api.factors.verify(
                    user_id, factor_id, transaction_id)
                status = verify.body['factorResult']
                wait_ct += 1
                if wait_ct > 15:
                    break
            if status != 'SUCCESS':
                response = {'status': 'UNAUTHORIZED'}
                return Response(json.dumps(response), 401)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
