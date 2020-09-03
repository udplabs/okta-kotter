import json
import logging
import time

from functools import wraps

import requests

from flask import Response, session, request
from jwcrypto import jwt, jwk, jws

from ...util import OktaAPIClient, UserFactorResource
from ...util.settings import app_settings

JWK_CACHE = []


def get_token_from_header():
    auth_header = request.headers.get('Authorization')
    type_, token = auth_header.split(' ')
    return token


# TODO: this should probably be a class that can take auth server params as config
def validate_access_token(token, scopes, user_id=None):
    global JWK_CACHE
    settings = app_settings()
    if len(JWK_CACHE) == 0:
        url = '{}/v1/keys'.format(settings['OKTA_ISSUER'])
        resp = requests.get(url)
        keys = json.loads(resp.content)['keys']
    else:
        keys = JWK_CACHE
    # verify token
    # TODO: use keyset 'add' since there could be multiple keys: jwk.JWKSet() (instead of using loop)
    for k in keys:
        try:
            key = jwk.JWK(**k)
            # NOTE: .verify() is implied by checking the claims with the key
            verified_token = jwt.JWT(key=key, jwt=token)
            break
        except jws.InvalidJWSSignature:
            # TODO: warning?
            pass

    # check claims
    claims = json.loads(verified_token.claims)
    if user_id:
        assert claims['uid'] == user_id
        # ensure user_id matches uid in access token
    # TODO: raise custom error to indicate scopes didn't match, other failures
    for scope in scopes:
        assert scope in claims['scp']

    allowed_clients = [settings['OKTA_CLIENT_ID'], settings['OKTA_ADMIN_CLIENT_ID']]
    # assert claims['cid'] in allowed_clients
    # TODO/FIXME: if using "developer" Blueprint, consult database of allowed clients
    assert claims['iss'] == settings['OKTA_ISSUER']
    assert claims['aud'] == settings['OKTA_AUDIENCE']
    return claims


def authorize(scopes=[], user_id=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                token = get_token_from_header()
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
            # NOTE: this has only been tested with Okta Verify Push
            user_id = session.get('user_id', None)
            if not user_id:  # must be client credentials; no MFA
                return f(*args, **kwargs)
            settings = app_settings()
            okta = OktaAPIClient(
                settings['OKTA_BASE_URL'],
                settings['OKTA_API_KEY']
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
