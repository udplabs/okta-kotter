import json

from flask import request, jsonify, render_template, url_for, redirect
from flask_cors import cross_origin
from ...util import APIClient
from ...util.settings import app_settings

from .models import Event

from ..admin.util import auth_o4o
from ..admin.views import admin_blueprint
from ..api.api import api_blueprint
from ...util.settings import app_settings


@admin_blueprint.route('/events', methods=('GET',))
@auth_o4o('admin.events')  # NOTE: requires okta.eventHooks.read
def events():
    settings = app_settings()
    api_url = '{}/api/v1'.format(settings['OKTA_BASE_URL'])
    okta = APIClient(api_url, request.cookies.get('o4o_token'))
    okta.api.add_resource(resource_name='eventHooks')
    data = okta.api.eventHooks.retrieve(settings['FF_EVENTS_HOOK_ID'])
    # print(json.dumps(data.body['events']['items']))
    admin_url_segs = settings['OKTA_BASE_URL'].split('.')
    admin_url = admin_url_segs[0] + '-admin.' + '.'.join(
        [admin_url_segs[1], admin_url_segs[2]])
    return render_template(
        'events/index.html',
        hooks=data.body['events']['items'],
        admin_url=admin_url,
        config=app_settings()
    )


@api_blueprint.route('/events', methods=['GET', 'POST'])  # noqa
@cross_origin()  # TODO: whitelist Okta domain
def events_api():
    event_obj = Event()
    if request.method == 'POST':
        data = json.loads(request.get_data())
        event = data['data']['events'][0]
        obj = {
            'eventType': event['eventType'],
            'displayMessage': event['displayMessage'],
            'severity': event['severity'],
            'ipAddress': event['client']['ipAddress'],
            'published': event['published'],
            'uuid': event['uuid'],
        }
        event_obj.add(obj)
    else:
        event_hook_verify_code = request.headers.get(
            'X-Okta-Verification-Challenge', None)
        if event_hook_verify_code:
            return json.dumps({'verification': event_hook_verify_code})
        data = event_obj.all()
    return jsonify(data)


@admin_blueprint.route('/events-clear', methods=['GET'])
def events_clear():
    events = Event()
    events.purge()
    return redirect(url_for('admin.events'))
