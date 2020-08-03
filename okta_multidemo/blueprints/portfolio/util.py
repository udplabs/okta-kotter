from functools import wraps

from flask import request, current_app
from werkzeug.exceptions import Unauthorized
from simple_rest_client.resource import Resource

from ...util import decode_token, get_api_default_actions, APIClient


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


class GrantResource(Resource):
    actions = get_api_default_actions('users')
    actions.update({
        'list': {'method': 'GET', 'url': 'users/{}/grants'},
        'delete': {'method': 'DELETE', 'url': 'users/{}/grants/{}'},
    })


def get_api_client():
    api_url = '{}/api/v1'.format(current_app.config['OKTA_BASE_URL'])
    okta = APIClient(api_url, request.cookies.get('o4o_token'))
    okta.api.add_resource(
        resource_name='grants',
        resource_class=GrantResource
    )
    return okta.api
