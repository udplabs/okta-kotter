import json

from flask import Blueprint, request, jsonify, session, current_app, Response, render_template
from tinydb import TinyDB, Query
from simple_rest_client.exceptions import AuthError
from werkzeug.exceptions import Unauthorized

from ..util import APIClient, OktaAPIClient, decode_token

from .util import auth_admin

admin_blueprint = Blueprint('admin', 'admin', url_prefix='/admin')


@admin_blueprint.route('/', methods=('GET',))
@auth_admin()
def index():
    return render_template(
        'admin/index.html'
    )


@admin_blueprint.route('/orders', methods=('GET',))
@auth_admin()
def orders():
    client = APIClient(current_app.config['API_URL'], request.cookies.get('access_token'))
    client.api.add_resource(resource_name='orders')
    try:
        data = client.api.orders.list()
    except AuthError:
        raise Unauthorized
    return render_template(
        'admin/orders.html',
        orders=data.body
    )


@admin_blueprint.route('/users', methods=('GET',))
@auth_admin()
def users():
    okta = OktaAPIClient(
        current_app.config['OKTA_BASE_URL'],
        current_app.config['OKTA_API_KEY']
    )
    okta.api.add_resource(resource_name='users')
    # TODO: get only users assigned to app
    data = okta.api.users.list()
    return render_template(
        'admin/users.html',
        users=data.body
    )
