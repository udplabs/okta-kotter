import json

from flask import Blueprint, request, jsonify, session, current_app, Response, render_template, redirect, url_for, flash
from tinydb import TinyDB, Query
from simple_rest_client.exceptions import AuthError
from werkzeug.exceptions import Unauthorized
from tinydb import TinyDB

from ...util import APIClient, OktaAPIClient, decode_token

from .util import authorize, PolicyResource
from .forms import ClientForm
from .models import Client

developer_blueprint = Blueprint('developer', 'developer', url_prefix='/developer')


@developer_blueprint.route('/', methods=('GET',))
@authorize()
def index(user_id=None):
    clients = Client()
    clients = clients.all()
    return render_template(
        'blueprints/developer/index.html',
        clients=clients
    )


# TODO: REST-ify clients

@developer_blueprint.route('/create-client', methods=('GET', 'POST'))
@authorize()
def create_client(user_id=None):
    form = ClientForm()
    if request.method == 'POST':
        if form.validate():
            client_name = form.name.data
            grant_type = form.grant_type.data
            params = {
                'client_name': client_name,
                'grant_types': [grant_type]
            }

            # hit API: create client
            # TODO: move to util.py?
            okta = OktaAPIClient(
                current_app.config['OKTA_BASE_URL'],
                current_app.config['OKTA_API_KEY'],
                'oauth2'
            )
            okta.api.add_resource(resource_name='clients')
            if grant_type == 'client_credentials':
                params.update({
                    'application_type': 'service',
                    'response_types': ['token'],
                })
            else: # authorization code
                # TODO: not tested
                params.update({
                    'application_type': 'web',
                    'response_types': ['id_token', 'code'],
                    'redirect_uris': [form.redirect_uri.data],
                })
            result = okta.api.clients.create(body=params)
            client_id = result.body['client_id']
            client_secret = result.body['client_secret']

            # hit API: add client to access policy
            okta = OktaAPIClient(
                current_app.config['OKTA_BASE_URL'],
                current_app.config['OKTA_API_KEY'],
            )
            okta.api.add_resource(
                resource_name='policies',
                resource_class=PolicyResource
            )
            authz_server_id = current_app.config['OKTA_ISSUER'].split('/')[-1]
            policy_id = current_app.config['FF_DEVELOPER_CC_POLICY_ID']
            result = okta.api.policies.get(authz_server_id, policy_id)
            policy = result.body
            client_ids = result.body['conditions']['clients']['include']
            client_ids.append(client_id)
            policy.update({
                'conditions': {'clients': {'include': client_ids}}
            })
            okta.api.policies.update(authz_server_id, policy_id, body=policy)

            # save to local DB
            clients = Client()
            params.update({
                'user_id': user_id,
                'client_id': client_id,
                'client_secret': client_secret,
            })
            result = clients.add(params)

            return redirect(url_for('developer.index'))
        else:
            flash('Invalid form data.')
    resp = render_template('blueprints/developer/form.html', form=form)
    return resp


@developer_blueprint.route('/delete-client', methods=('GET',))
@authorize()
def delete_client(user_id=None):
    okta = OktaAPIClient(
        current_app.config['OKTA_BASE_URL'],
        current_app.config['OKTA_API_KEY'],
        'oauth2'
    )
    local_id = request.args.get('id')
    client_id = request.args.get('client_id')
    okta.api.add_resource(resource_name='clients')
    okta.api.clients.destroy(client_id)
    clients = Client()
    # FIXME: should be able to use local_id
    result = clients.delete('client_id', client_id)
    print(result)

    return redirect(url_for('developer.index'))
