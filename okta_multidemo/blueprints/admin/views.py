from flask import Blueprint, request, render_template

from ...models import Order
from ...util import APIClient
from ...util.settings import app_settings

from .util import auth_admin, auth_o4o

admin_blueprint = Blueprint('admin', 'admin', url_prefix='/admin')


@admin_blueprint.route('/', methods=('GET',))
@auth_admin()
def index():
    settings = app_settings()
    return render_template(
        'admin/index.html',
        config=settings
    )


@admin_blueprint.route('/orders', methods=('GET',))
@auth_admin()
def orders():
    settings = app_settings()
    status = request.args.get('status')
    orders = Order()
    if status:
        data = orders.get({'status': status})
    else:
        data = orders.get()
    return render_template(
        'admin/orders.html',
        orders=data,
        config=settings
    )


@admin_blueprint.route('/users', methods=('GET',))
@auth_o4o('admin.users')
def users():
    # get users via OAuth for Okta instread of SSWS API key
    settings = app_settings()
    api_url = '{}/api/v1'.format(settings['OKTA_BASE_URL'])
    okta = APIClient(api_url, request.cookies.get('o4o_token'))
    okta.api.add_resource(resource_name='users')
    # TODO: get only users assigned to app
    data = okta.api.users.list()
    return render_template(
        'admin/users.html',
        users=data.body,
        config=settings
    )


@admin_blueprint.route('/config', methods=('GET',))
@auth_admin()
def config():
    settings = app_settings()
    return render_template(
        'admin/config.html',
        config=settings
    )
