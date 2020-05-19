import json
from functools import wraps

from flask import session, request
from werkzeug.exceptions import Unauthorized
from simple_rest_client.resource import Resource

from ...util import decode_token, get_api_default_actions, OktaAPIClient
from .models import Client


def authorize():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            access_token = request.cookies.get('access_token')
            # TODO: actually validate token, since we're not using an API endpoint
            if not access_token:
                raise Unauthorized
            access_decoded = decode_token(access_token)
            kwargs.update({'user_id': access_decoded['uid']})
            return f(*args, **kwargs)
        return decorated_function
    return decorator


class PolicyResource(Resource):
    actions = get_api_default_actions('policies')
    actions.update({
        'get': {'method': 'GET', 'url': 'authorizationServers/{}/policies/{}'},
        'update': {'method': 'PUT', 'url': 'authorizationServers/{}/policies/{}'},
    })


class AppGroupResource(Resource):
    actions = {
        'assign': {'method': 'PUT', 'url': 'apps/{}/groups/{}'},
    }
    actions.update(get_api_default_actions('apps'))


def add_client_to_policy(client_id, policy_id, config):
    okta = OktaAPIClient(
        config['OKTA_BASE_URL'],
        config['OKTA_API_KEY'],
    )
    okta.api.add_resource(
        resource_name='policies',
        resource_class=PolicyResource
    )
    authz_server_id = config['OKTA_ISSUER'].split('/')[-1]
    result = okta.api.policies.get(authz_server_id, policy_id)
    policy = result.body
    client_ids = result.body['conditions']['clients']['include']
    client_ids.append(client_id)
    policy.update({
        'conditions': {'clients': {'include': client_ids}}
    })
    okta.api.policies.update(authz_server_id, policy_id, body=policy)


def create_cc_client(client_name, grant_type, user_id, redirect_uri, config):
    params = {
        'client_name': client_name,
        'grant_types': [grant_type]
    }

    # create client in Okta
    okta = OktaAPIClient(
        config['OKTA_BASE_URL'],
        config['OKTA_API_KEY'],
        'oauth2'
    )
    okta.api.add_resource(resource_name='clients')
    params.update({
        'application_type': 'service',
        'response_types': ['token'],
    })
    result = okta.api.clients.create(body=params)
    client_id = result.body['client_id']
    client_secret = result.body['client_secret']

    add_client_to_policy(
        client_id, config['FF_DEVELOPER_CC_POLICY_ID'], config)

    # save to local DB
    clients = Client()
    params.update({
        'user_id': user_id,
        'client_id': client_id,
        'client_secret': client_secret,
    })
    clients.add(params)


def create_pkce_client(client_name, user_id, group_id, redirect_uri, config):
    okta = OktaAPIClient(
        config['OKTA_BASE_URL'],
        config['OKTA_API_KEY']
    )
    params_db = {
        'client_name': client_name,
        'grant_types': ['authorization_code']
    }
    params = {
        "name": "oidc_client",
        "label": client_name,
        "signOnMode": "OPENID_CONNECT",
        "credentials": {
            "oauthClient": {
                "token_endpoint_auth_method": "none"
            }
        },
        "settings": {
            "oauthClient": {
                "client_uri": redirect_uri,  # same as redirect URI for simplicity
                "redirect_uris": [
                    redirect_uri
                ],
                "response_types": [
                    "code"
                ],
                "grant_types": [
                    "authorization_code",
                    "refresh_token"
                ],
                "application_type": "native",
                "consent_method": "REQUIRED"
            }
        }
    }
    okta.api.add_resource(resource_name='apps')
    result = okta.api.apps.create(body=params)
    client_id = result.body['id']

    # assign group to app
    okta.api.add_resource(
        resource_name='app_groups',
        resource_class=AppGroupResource
    )
    okta.api.app_groups.assign(client_id, group_id)

    add_client_to_policy(
        client_id, config['FF_DEVELOPER_PKCE_POLICY_ID'], config)

    # save to local DB
    clients = Client()
    params_db.update({
        'user_id': user_id,
        'client_id': client_id,
        'client_secret': '',
    })
    clients.add(params_db)
    # TODO: log creation of client for easier deletion
