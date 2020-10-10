# -*- coding: utf-8 -*-
import logging
from urllib.parse import urlparse

from flask import Flask, render_template, request, session, g
from tinydb import TinyDB
from tinydb.storages import MemoryStorage


# TODO: rename/reorg blueprints for consistency
from .blueprints.auth.views import auth_blueprint
from .blueprints.api.api import api_blueprint
from .blueprints.admin.views import admin_blueprint
from .blueprints.developer.views import developer_blueprint
from .blueprints.portfolio.views import portfolio_blueprint
from .blueprints.events import views
from .logs import configure_logging
from .util import init_db, get_help_markdown

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
    if not hasattr(g, 'db'):
        if app.config['DB_PATH']:
            g.db = TinyDB(app.config['DB_PATH'])
        else:
            g.db = TinyDB(storage=MemoryStorage)
    if request.path.startswith('/static') \
            or request.path.startswith('/api') \
            or request.path == ('/favicon.ico'):
        return

    # init db for subdomain
    subdomain = urlparse(request.url).hostname.split('.')[0]
    session_subdomain = session.get('subdomain', None)
    if not session_subdomain:
        session['subdomain'] = subdomain
        init_db(g.db, app.config['ENV'], subdomain)

    # handle help URLs
    if request.path.endswith('/'):
        path = request.path + 'index'
    else:
        path = request.path[1:]
    try:
        g.help = get_help_markdown(path, session, request)

    except FileNotFoundError:
        logging.warning('No help file found for {} view'.format(path))


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
