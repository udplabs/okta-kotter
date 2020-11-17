from flask import Blueprint, request, render_template, flash

from ...models import get_model
from ...util import APIClient, OktaAPIClient
from ...util.settings import app_settings
from ...util.decorators import login_required

from ..developer.util import PolicyResource
from .util import auth_admin, auth_o4o

admin_blueprint = Blueprint('admin', 'admin', url_prefix='/admin')


@admin_blueprint.route('/', methods=('GET',))
@login_required
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
    orders = get_model('orders')
    if status:
        data = orders.get({'status': status})
    else:
        data = orders.all()
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
    if not settings['OKTA_API_KEY']:
        flash(
          'No Okta API key configured. See <a href="https://github.com/udplabs/okta-kotter/tree/master/docs/udp">this documentation</a> for additional configuration information.',
          'danger'
        )
        groups = []
        as_data = []
        event_hooks = []
    else:
        okta = OktaAPIClient(settings['OKTA_BASE_URL'], settings['OKTA_API_KEY'])
        # groups, auth servers + policies, event hooks

        okta.api.add_resource(resource_name='groups')
        groups = okta.api.groups.list().body

        okta.api.add_resource(resource_name='authorizationServers')
        okta.api.add_resource(resource_name='policies', resource_class=PolicyResource)
        as_data = []
        auth_svrs = okta.api.authorizationServers.list()
        for i in auth_svrs.body:
            policies = okta.api.policies.get(i['id'], '').body
            as_data.append({
                'name': i['name'],
                'id': i['id'],
                'issuer': i['issuer'],
                'policies': [{'name': j['name'], 'id': j['id']} for j in policies]
            })

        okta.api.add_resource(resource_name='eventHooks')
        event_hooks = okta.api.eventHooks.list().body

    return render_template(
        'admin/config.html',
        config=settings,
        groups_data=groups,
        as_data=as_data,
        hooks_data=event_hooks
    )
