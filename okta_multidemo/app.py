# -*- coding: utf-8 -*-
import logging

import simple_rest_client
from urllib.parse import urlparse
from flask import Flask, render_template, request, session, g
from jinja2.exceptions import TemplateNotFound

# TODO: rename/reorg blueprints for consistency
from .blueprints.auth.views import auth_blueprint
from .blueprints.api.api import api_blueprint
from .blueprints.admin.views import admin_blueprint
from .blueprints.developer.views import developer_blueprint
from .blueprints.portfolio.views import portfolio_blueprint
from .blueprints.events import views
from .logs import configure_logging
from .util import init_db, get_help_markdown
from .models import get_db

app = Flask(__name__)
app.secret_key = app.config['SECRET_KEY']
configure_logging()

app.static_folder = 'static'
app.add_url_rule('/static/<path:filename>',
                 endpoint='static',
                 subdomain='<tenant>',
                 view_func=app.send_static_file)

if app.config['ENV'] == 'production':  # reads from FLASK_ENV env variable
    app.config.from_object('okta_multidemo.config.ProductionConfig')
else:  # 'development'
    app.config.from_object('okta_multidemo.config.DevelopmentConfig')

# TODO: need to import after app.config takes place -- is this ok?
from . import views  # noqa


@app.before_request
def before_request():
    global app

    # NOTE: normally excluding static assets would be handled by the webserver,
    #   and API would be a different app on a different domain
    if request.path.startswith('/static') \
            or request.path.startswith('/api') \
            or request.path == ('/favicon.ico'):
        return

    # init db for subdomain
    subdomain = urlparse(request.url).hostname.split('.')[0]
    session_subdomain = session.get('subdomain', None)
    if not session_subdomain:
        session['subdomain'] = subdomain
        init_db(app.config['ENV'], subdomain)


@app.teardown_appcontext
def close_db(error):
    """Closes database end of the request."""
    if hasattr(g, 'db'):
        try:
            g.db.close()
        except:
            logging.debug('Failed to close DB')


@app.template_filter()
def get_help_template(path):
    if path == '/':
        template_path = 'index.html'
    else:
        if path.endswith('/'):
            path = path[:-1]
        template_path = path + '.html'
    return('help/' + template_path)


# TODO: refactor error page handlers to a single function
def page_not_found(e):
    return render_template('404.html'), 404


def server_error(e):
    return render_template('500.html'), 500


def unauthorized(e):
    return render_template('401.html'), 401


def forbidden(e):
    return render_template('403.html'), 403


blueprints = [
    auth_blueprint,
    api_blueprint,
    admin_blueprint,
    developer_blueprint,
    portfolio_blueprint
]

for blueprint in blueprints:
    app.register_blueprint(blueprint)

app.register_error_handler(404, page_not_found)
app.register_error_handler(500, server_error)
app.register_error_handler(401, unauthorized)
app.register_error_handler(403, forbidden)


@app.errorhandler(simple_rest_client.exceptions.AuthError)
def handle_rest_auth_error(e):
    return render_template('401.html'), 401
