import json
import logging

import pytz
import requests

from dateutil.parser import parse
from flask import render_template, request, make_response, url_for, redirect, flash, session, current_app, Response
from simple_rest_client import exceptions
from werkzeug.exceptions import Unauthorized

from . import filters
from .app import app
from .forms import LoginForm, ProfileForm
from .logs import format_json_output
from .models import Product
from .util import APIClient, decode_token, OktaAPIClient, get_help_markdown
from .util.widget import get_widget_config


def set_session_vars(access_token, id_token):
    access_decoded = decode_token(access_token)
    id_decoded = decode_token(id_token)
    session['username'] = id_decoded['email']
    session['name'] = id_decoded['name']
    session['user_id'] = id_decoded['sub']
    session['is_admin'] = 'Admin' in id_decoded['groups']
    session['access_token'] = access_token
    session['id_token'] = id_token


@app.route('/', methods=['GET', 'POST'])
def index():
    access_token = session.get('access_token', request.cookies.get('access_token'))
    id_token = session.get('id_token', request.cookies.get('id_token'))
    token_dict = {}
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
    resp = make_response(render_template(
        'index.html',
        data=token_dict,
        body_class='home-body-image'
    ))
    return resp


@app.route('/authorization/redirect')
def authorization_redirect():
    # authz flow only
    blueprint = request.args.get('conf', 'okta')
    token_dict = {}
    token_main = app.blueprints[blueprint].session.token
    if not token_main:
        raise Unauthorized
    access_token = token_main['access_token']
    id_token = token_main['id_token']
    set_session_vars(access_token, id_token)
    if blueprint == 'okta-admin':
        resp = redirect(url_for('admin.index'))
    else:
        resp = redirect(url_for('index'))
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


def render_login_template(conf, css=None):
    resp = render_template(
        'login/widget.html',
        widget_conf=json.dumps(conf, indent=2),
        body_class='home-body-image' if not css else 'home-body-bgcolor',
        custom_css=css
    )
    return resp


@app.route('/login-widget', methods=['GET'])
def login_widget():
    conf = get_widget_config(current_app.config)
    return render_login_template(conf)


@app.route('/login-social', methods=['GET'])
def login_widget_social():
    conf = get_widget_config(current_app.config, 'social')
    return render_login_template(conf)


@app.route('/login-implicit', methods=['GET'])
def login_widget_implicit():
    conf = get_widget_config(current_app.config, 'implicit')
    return render_login_template(conf)


@app.route('/login-custom-css', methods=['GET'])
def login_widget_custom_css():
    conf = get_widget_config(current_app.config)
    return render_login_template(conf, css='okta-signin-custom')


@app.route('/login-idp-disco', methods=['GET'])
def login_idp_disco():
    conf = get_widget_config(current_app.config, 'idp-disco')
    return render_login_template(conf)


@app.route('/login-custom', methods=['GET'])
def login_custom():
    resp = render_template('login/custom.html', form=LoginForm())
    return resp


@app.route('/implicit/callback', methods=['POST'])
def implicit_callback():
    # if request.form:
    #     access_token = request.form['access_token']
    #     id_token = request.form['id_token']
    # else:
    data = json.loads(request.data)
    access_token = data[0]['accessToken']
    id_token = data[1]['idToken']
    set_session_vars(access_token, id_token)
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
    id_token = session.get('id_token', request.cookies.get('id_token'))
    logout_url = '{}/v1/logout?id_token_hint={}&post_logout_redirect_uri={}'.format(
        app.config['OKTA_ISSUER'],
        id_token,
        app.config['APP_URL']
    )
    resp = redirect(logout_url)
    # resp = make_response(redirect(url_for('index')))
    # ^^^ use this instead to avoid killing Okta session
    resp.set_cookie('access_token', '', expires=0)
    resp.set_cookie('id_token', '', expires=0)
    session.clear()
    return resp


@app.route(app.config['ITEMS_PATH'], methods=('GET',))
def products():
    # NOTE: Here the view calls the REST API, rather than importing the model directly.
    #   In an MVC app it doesn't have to work this way.
    client = APIClient(app.config['API_URL'], request.cookies.get('access_token'))
    client.api.add_resource(resource_name='products')
    try:
        data = client.api.products.list()
    except exceptions.AuthError:
        raise Unauthorized
    if current_app.config['ITEMS_IMG']:
        img_path = '{}/img-items/'.format(current_app.config['THEME_URI'])
    else:
        img_path = '{}/static/img/items/'.format(current_app.config['APP_URL'])
    return render_template(
        'products.html',
        items=data.body,
        img_path=img_path
    )


@app.route('/apps', methods=('GET',))
def apps():
    okta = OktaAPIClient(
        current_app.config['OKTA_BASE_URL'],
        current_app.config['OKTA_API_KEY']
    )
    okta.api.add_resource(resource_name='apps')
    print(session['user_id'])
    data = okta.api.apps.list(params={
        'filter': 'user.id eq "{}"'.format(session['user_id']),
        'limit': 100
    })
    return render_template(
        'apps.html',
        apps=data.body
    )


@app.route('{}-rest'.format(app.config['ITEMS_PATH']), methods=('GET',))
def products_rest():
    if current_app.config['ITEMS_IMG']:
        img_path = '{}/img-items/'.format(current_app.config['THEME_URI'])
    else:
        img_path = '{}/static/img/items/'.format(current_app.config['APP_URL'])
    return render_template('products-rest.html', img_path=img_path)
