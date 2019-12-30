import json
import logging

import feedparser
import requests
import pytz

from dateutil.parser import parse

from flask import render_template, request, make_response, url_for, redirect, flash, session, current_app, Response
from werkzeug.exceptions import Unauthorized
from simple_rest_client import exceptions

from .app import app
from . import filters
from .forms import LoginForm, ProfileForm
from .models import Item
from .logs import format_json_output
from .util import APIClient, decode_token
from .util.widget import get_widget_config


@app.route('/', methods=['GET', 'POST'])
def index():
    token_dict = {}
    token_main = app.blueprints['okta'].session.token  # only used with authz flow

    access_token = None
    id_token = None
    if token_main:
        access_token = token_main['access_token']
        id_token = token_main['id_token']
    else:
        access_token = request.cookies.get('access_token')
        id_token = request.cookies.get('id_token')
    if access_token:
        access_decoded = decode_token(access_token)
        id_decoded = decode_token(id_token)
        access_payload_fmt = json.dumps(access_decoded, indent=4)
        id_payload_fmt = json.dumps(id_decoded, indent=4)
        token_dict = {
            'id': {
                'token': id_token,
                'payload': id_payload_fmt,
            },
            'access': {
                'token': access_token,
                'payload': access_payload_fmt,
            },
        }
        session['username'] = id_decoded['email']
        session['name'] = id_decoded['name']
        session['user_id'] = id_decoded['sub']
        # logging.debug(format_json_output(id_decoded))

    resp = make_response(render_template(
        'index.html',
        help={'name': 'tokens', 'data': token_dict}
    ))
    if token_main:
        # NOTE: we're putting the tokens in the cookie so that the client
        #   can access API endpoints.  A more secure MVC app might
        #   manage them on the server side, while a SPA app might
        #   use the token manager of the Okta Auth SDK to manage them
        #   in local storage.
        resp.set_cookie('access_token', access_token)
        resp.set_cookie('id_token', id_token)
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
    conf = get_widget_config(current_app.config)
    resp = render_template('login/widget.html',
        widget_conf=json.dumps(conf, indent=2))
    return resp


@app.route('/login-social', methods=['GET'])
def login_widget_social():
    conf = get_widget_config(current_app.config, 'social')
    resp = render_template('login/widget.html',
        widget_conf=json.dumps(conf, indent=2))
    return resp


@app.route('/login-implicit', methods=['GET'])
def login_widget_implicit():
    conf = get_widget_config(current_app.config, 'implicit')
    resp = render_template('login/widget.html',
        widget_conf=json.dumps(conf, indent=2))
    return resp


@app.route('/implicit/callback', methods=['POST'])
def implicit_callback():
    data = json.loads(request.data)
    access_token = data[0]['accessToken']
    id_token = data[1]['idToken']
    resp = make_response(Response(json.dumps({'status': 'OK'}), 200)) # redirect(url_for('index'))
    resp.set_cookie('access_token', access_token)
    resp.set_cookie('id_token', id_token)
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
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('access_token', '', expires=0)
    resp.set_cookie('id_token', '', expires=0)
    session.clear()
    return resp


@app.route(app.config['ITEMS_PATH'], methods=('GET',))
def items():
    # NOTE: Here the view calls the REST API, rather than the model directly.
    #   In an MVC app it doesn't have to work this way.
    # import pdb;pdb.set_trace()
    client = APIClient(app.config['API_URL'], request.cookies.get('access_token'))
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
