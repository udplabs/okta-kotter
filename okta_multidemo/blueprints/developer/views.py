"""TODO: docstring."""
import json

import requests

from flask import (
    Blueprint, request, current_app, render_template, redirect, url_for, flash)
from requests.auth import HTTPBasicAuth

from ...util import OktaAPIClient

from .util import authorize, create_cc_client, create_pkce_client
from .forms import ClientForm
from .models import Client

developer_blueprint = Blueprint(
    'developer', 'developer', url_prefix='/developer')


@developer_blueprint.route('/', methods=('GET',))
@authorize()
def index(user_id=None):
    """TODO: docstring."""
    client = Client()
    clients = client.all()
    return render_template(
        'blueprints/developer/index.html',
        clients=clients
    )


# TODO: REST-ify clients

@developer_blueprint.route('/create-client', methods=('GET', 'POST'))
@authorize()
def create_client(user_id=None):
    """TODO: docstring."""
    form = ClientForm()
    if request.method == 'POST':
        if form.validate():
            client_name = form.name.data
            grant_type = form.grant_type.data
            if grant_type == 'client_credentials':
                create_cc_client(
                    current_app.config['OKTA_RESOURCE_PREFIX'] + client_name,
                    grant_type,
                    user_id,
                    form.redirect_uri.data,
                    current_app.config
                )
            else:  # PKCE
                create_pkce_client(
                    current_app.config['OKTA_RESOURCE_PREFIX'] + client_name,
                    user_id,
                    current_app.config['FF_PORTFOLIO_CLIENT_GROUP'],
                    form.redirect_uri.data,
                    current_app.config)
            return redirect(url_for('developer.index'))
        else:
            flash('Invalid form data.')
    resp = render_template('blueprints/developer/form.html', form=form)
    return resp


@developer_blueprint.route('/delete-client', methods=('GET',))
@authorize()
def delete_client(user_id=None):
    """TODO: docstring."""
    okta = OktaAPIClient(
        current_app.config['OKTA_BASE_URL'],
        current_app.config['OKTA_API_KEY'],
        'oauth2'
    )
    client_id = request.args.get('client_id')
    okta.api.add_resource(resource_name='clients')
    okta.api.clients.destroy(client_id)
    clients = Client()
    # FIXME: should be able to use local_id
    clients.delete('client_id', client_id)
    return redirect(url_for('developer.index'))


@developer_blueprint.route('/test-client', methods=('POST',))
@authorize()
def test_client(user_id=None):
    """TODO: docstring."""
    client_id = request.form['client_id']
    client_secret = request.form['client_secret']
    client_name = request.form['client_name']
    url = '{}/v1/token'.format(current_app.config['OKTA_ISSUER'])
    auth = HTTPBasicAuth(client_id, client_secret)
    headers = {
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
    }
    data = {
        'grant_type': 'client_credentials',
        'scope': 'products:read',
    }
    req = requests.post(
        url,
        headers=headers,
        data=data,
        auth=auth
    )
    resp = render_template(
        'blueprints/developer/test.html',
        token_resp=json.dumps(req.json()),
        client_id=client_id,
        client_secret=client_secret,
        client_name=client_name
    )
    return resp
