import json
import logging

import feedparser
import requests
import pytz
import jwt

from dateutil.parser import parse

from flask import render_template, request, make_response, url_for, redirect, flash, session, current_app
from werkzeug.exceptions import Unauthorized
from simple_rest_client import exceptions

from .app import app
from . import filters
from .forms import LoginForm, ProfileForm
from .models import Item
from .logs import format_json_output
from .util import APIClient


@app.route('/', methods=['GET', 'POST'])
def index():
    token = app.blueprints['okta'].session.token
    token_dict = {}

    if token:
        access_decoded = jwt.decode(token['access_token'], verify=False)
        id_decoded = jwt.decode(token['id_token'], verify=False)
        access_payload_fmt = json.dumps(access_decoded, indent=4)
        id_payload_fmt = json.dumps(id_decoded, indent=4)
        token_dict = {
            'id': {
                'token': token['id_token'],
                'payload': id_payload_fmt,
            },
            'access': {
                'token': token['access_token'],
                'payload': access_payload_fmt,
            },
        }
        session['username'] = id_decoded['email']
        session['name'] = id_decoded['name']
        session['user_id'] = id_decoded['sub']
        logging.debug(format_json_output(id_decoded))

    resp = make_response(render_template(
        'index.html',
        help={'name': 'tokens', 'data': token_dict}
    ))
    if token:
        resp.set_cookie('access_token', token_dict['access']['token'])
    return resp


@app.route('/login', methods=['GET', 'POST'])
def login_form():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate():
            params = {
                'email': form.username.data,
                'password': form.password.data,
            }
            req = requests.post('https://groups.io/api/v1/login', data=params)
            if req.status_code != 200:
                flash('Login failed.')
            else:
                resp = redirect(url_for('index'))
                cookies = dict(zip(req.cookies.keys(), req.cookies.values()))
                for key in cookies.keys():
                    resp.set_cookie(key, cookies[key])
                session['username'] = req.json()['user']['email']
                session['full_name'] = req.json()['user']['full_name']
                session['csrf'] = req.json()['user']['csrf_token']
                flash('Welcome {}!'.format(req.json()['user']['email']))
                if not session['full_name']:
                    flash(
                        'You have not yet set your display name. Please click on your email address in the upper right.',
                        'warning'
                    )
                return resp
        else:
            flash('Invalid form data.')
    resp = render_template('login.html', form=form)
    return resp


@app.route('/login-widget', methods=['GET'])
def login_widget():
    resp = render_template('login/widget.html')
    return resp


@app.route('/login-social', methods=['GET'])
def login_widget_social():
    social = True
    resp = render_template('login/widget.html', social=social)
    return resp


@app.route('/subscribe', methods=['GET'])
def subscribe():
    resp = render_template('subscribe.html')
    return resp


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = ProfileForm(display_name=session.get('full_name', ''))
    if request.method == 'POST':
        if form.validate():
            params = {
                'full_name': form.display_name.data,
                'csrf': session['csrf'],
            }
            req = requests.post('https://groups.io/api/v1/updateprofile', data=params, cookies=request.cookies)
            if req.status_code != 200:
                flash('Update failed.')
            else:
                resp = redirect(url_for('profile'))
                session['full_name'] = form.display_name.data
                flash('Profile updated!')
                return resp
        else:
            flash('Invalid form data.')
    resp = render_template('profile.html', form=form)
    return resp


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    resp = redirect(url_for('index'))
    return resp


@app.route(app.config['ITEMS_PATH'], methods=('GET',))
def items():
    # NOTE: Here the view calls the REST API, rather than the model directly.
    #   In an MVC app it doesn't have to work this way.
    client = APIClient(app.config['API_URL'], session['okta_oauth_token']['access_token'])
    client.api.add_resource(resource_name='items')
    try:
        data = client.api.items.list()
    except exceptions.AuthError:
        raise Unauthorized
    return render_template(
        'items.html',
        items=data.body
    )


@app.route('{}-spa'.format(app.config['ITEMS_PATH']), methods=('GET',))
def items_spa():
    return render_template('items-spa.html')
