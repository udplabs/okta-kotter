import json

from flask import request, jsonify, render_template, current_app
from flask_cors import cross_origin
from ...util import APIClient

from .models import Event

from ..admin.util import auth_admin, auth_o4o
from ..admin.views import admin_blueprint
from ..api.api import api_blueprint


@admin_blueprint.route('/events', methods=('GET',))
@auth_o4o()  # NOTE: requires okta.eventHooks.read
def events():
    api_url = '{}/api/v1'.format(current_app.config['OKTA_BASE_URL'])
    okta = APIClient(api_url, request.cookies.get('o4o_token'))
    okta.api.add_resource(resource_name='eventHooks')
    data = okta.api.eventHooks.retrieve(current_app.config['FF_EVENTS_HOOK_ID'])
    # print(json.dumps(data.body['events']['items']))
    return render_template(
        'events/index.html',
        hooks=data.body['events']['items']
    )


@api_blueprint.route('/events', methods=['GET', 'POST'])  # noqa
@cross_origin()  # TODO: whitelist Okta domain
def events_api():
    event_obj = Event()
    if request.method == 'POST':
        data = json.loads(request.get_data())
        print(data)
        event = data['data']['events'][0]
        obj = {
            'eventType': event['eventType'],
            'displayMessage': event['displayMessage'],
            'severity': event['severity'],
            'ipAddress': event['client']['ipAddress'],
            'published': event['published'],
            'uuid': event['uuid'],
        }
        print(json.dumps(obj))
        event_obj.add(obj)
    else:
        event_hook_verify_code = request.headers.get(
            'X-Okta-Verification-Challenge', None)
        if event_hook_verify_code:
            return json.dumps({'verification': event_hook_verify_code})
        data = event_obj.all()
    return jsonify(data)
