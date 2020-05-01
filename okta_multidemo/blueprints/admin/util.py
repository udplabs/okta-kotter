from functools import wraps

from flask import current_app, redirect, url_for


def auth_admin():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_app.blueprints['okta-admin'].token:
                resp = redirect(url_for('okta-admin.login'))
                return resp
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def auth_o4o():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_app.blueprints['okta-o4o'].token:
                resp = redirect(url_for('okta-o4o.login'))
                return resp
            return f(*args, **kwargs)
        return decorated_function
    return decorator
