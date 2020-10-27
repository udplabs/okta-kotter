"""TODO: docstring."""
import json

import requests

from flask import (
    Blueprint, request, render_template, redirect, url_for, flash)
from requests.auth import HTTPBasicAuth

from ...util import OktaAPIClient
from ...util.settings import app_settings

from .util import authorize, create_cc_client, create_pkce_client
from .forms import ClientForm
from ...models import get_model

developer_blueprint = Blueprint(
    'developer', 'developer', url_prefix='/developer')

# NOTE: the reason we store clients in the DB instead of just
#   getting them from Okta is to be able to persist the client secret


@developer_blueprint.route('/', methods=('GET',))
@authorize()
def index(user_id=None):
    """TODO: docstring."""
    settings = app_settings()
    client = get_model('clients')
    clients = client.all()
    for i in clients:
        i.update(
            {'client_name': i['client_name'].replace(
                settings['OKTA_RESOURCE_PREFIX'], ''
            )}
        )
    return render_template(
        'blueprints/developer/index.html',
        clients=clients,
        config=settings
    )


# TODO: REST-ify clients

@developer_blueprint.route('/create-client', methods=('GET', 'POST'))
@authorize()
def create_client(user_id=None):
    """TODO: docstring."""
    settings = app_settings()
    form = ClientForm()
    if request.method == 'POST':
        if form.validate():
            client_name = form.name.data
            grant_type = form.grant_type.data
            if grant_type == 'client_credentials':
                create_cc_client(
                    settings['OKTA_RESOURCE_PREFIX'] + client_name,
                    grant_type,
                    user_id,
                    form.redirect_uri.data,
                    settings
                )
            else:  # PKCE
                create_pkce_client(
                    settings['OKTA_RESOURCE_PREFIX'] + client_name,
                    user_id,
                    settings['FF_PORTFOLIO_CLIENT_GROUP'],
                    form.redirect_uri.data,
                    settings)
            return redirect(url_for('developer.index'))
        else:
            flash('Invalid form data.')
    resp = render_template(
        'blueprints/developer/form.html', form=form, config=settings)
    return resp


@developer_blueprint.route('/delete-client', methods=('GET',))
@authorize()
def delete_client(user_id=None):
    """TODO: docstring."""
    settings = app_settings()
    okta = OktaAPIClient(
        settings['OKTA_BASE_URL'],
        settings['OKTA_API_KEY'],
        'oauth2'
    )
    client_id = request.args.get('client_id')
    okta.api.add_resource(resource_name='clients')
    okta.api.clients.destroy(client_id)
    clients = get_model('clients')
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
    url = '{}/v1/token'.format(app_settings()['OKTA_ISSUER'])
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
        client_name=client_name,
        config=app_settings()
    )
    return resp
