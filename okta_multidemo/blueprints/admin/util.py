from functools import wraps

from flask import current_app, redirect, url_for, request

from ...util import decode_token


def auth_admin():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            access_token = request.cookies.get('access_token')
            decoded = decode_token(access_token)
            if sorted(decoded['scp']) != sorted(
                    current_app.config['OKTA_ADMIN_SCOPES']):
                resp = redirect(
                    url_for('auth.login', conf='okta-admin', view=request.endpoint))
                return resp
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def auth_o4o(state):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            o4o_token = request.cookies.get('o4o_token', None)
            if not o4o_token:
                resp = redirect(
                    url_for('auth.login', conf='okta-o4o', view=request.endpoint))
                return resp
            return f(*args, **kwargs)
        return decorated_function
    return decorator
