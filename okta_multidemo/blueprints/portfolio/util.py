from functools import wraps

from flask import session, request
from werkzeug.exceptions import Unauthorized
from simple_rest_client.resource import Resource

from ...util import decode_token, get_api_default_actions


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
