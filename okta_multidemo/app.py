# -*- coding: utf-8 -*-
import logging
import os

from flask import Flask, render_template, request, session, flash, redirect, url_for, g

from flask_talisman import Talisman
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length

# TODO: rename/reorg blueprints for consistency
from .okta import okta_blueprint, okta_admin_blueprint
from .api.api import api_blueprint
from .admin.admin import admin_blueprint
from .logs import configure_logging
from .util import init_db, get_help_markdown

app = Flask(__name__)
app.secret_key = app.config['SECRET_KEY']
configure_logging()

if app.config['ENV'] == 'production':  # reads from FLASK_ENV env variable
    app.config.from_object('okta_multidemo.config.ProductionConfig')
    # Talisman(app, content_security_policy=None)
else:
    app.config.from_object('okta_multidemo.config.DevelopmentConfig')
init_db(app.config['DB_PATH'], app.config['THEME_MODE'], app.config['THEME'])

# TODO: need to import after app.config takes place -- is this ok?
from okta_multidemo import views


@app.before_request
def before_request():
    if request.path.startswith('/static') or request.path.startswith('/api'):
        return
    if request.path == '/':
        path = 'index'
    else:
        path = request.path[1:]
    try:
        g.help = get_help_markdown(path, session)
    except FileNotFoundError:
        logging.warning('No help file found for {} view'.format(path))


def page_not_found(e):
    return render_template('404.html'), 404


def server_error(e):
    return render_template('500.html'), 500


def unauthorized(e):
    return render_template('401.html'), 401


app.register_blueprint(okta_blueprint, url_prefix='/login')
app.register_blueprint(okta_admin_blueprint, url_prefix='/login')
app.register_blueprint(api_blueprint)
app.register_blueprint(admin_blueprint)

app.register_error_handler(404, page_not_found)
app.register_error_handler(500, server_error)
app.register_error_handler(401, unauthorized)
