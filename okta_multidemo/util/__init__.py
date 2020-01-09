import json
import os

import jwt

from simple_rest_client.api import API
from simple_rest_client.resource import Resource

from tinydb import TinyDB


def init_db(path, theme_mode, theme):
    try:
        os.remove(path)
    except OSError:
        pass
    db = TinyDB(path)
    table = db.table('items')
    # TODO: get relative to current module path
    # from pathlib import Path
    # path = Path(__file__).parent.absolute()
    with open('./okta_multidemo/conf/{}/{}/data.json'.format(theme_mode, theme)) as file_:
        data = file_.read()
    items = json.loads(data)
    table.insert_multiple(items)

    table = db.table('orders')
    with open('./okta_multidemo/conf/orders.json') as file_:
        data = file_.read()
    items = json.loads(data)
    table.insert_multiple(items)


# NOTE: this is a simple_rest_client kludge
def get_api_default_actions(resource):
    return {
      'create': {
        'method': 'POST',
        'url': resource
      },
      'destroy': {
        'method': 'DELETE',
        'url': '%s/{}' % resource
      },
      'list': {
        'method': 'GET',
        'url': resource
      },
      'partial_update': {
        'method': 'PATCH',
        'url': '%s/{}' % resource
      },
      'retrieve': {
        'method': 'GET',
        'url': '%s/{}' % resource
      },
      'update': {
        'method': 'PUT',
        'url': '%s/{}' % resource
      }
    }


class APIClient(object):
    def __init__(self, api_url, access_token):
        self.api = API(
            api_root_url=api_url,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(access_token),
            },
            timeout=10,
            json_encode_body=True,
        )


class OktaAPIClient(object):
    def __init__(self, org_url, api_key):
        self.api = API(
            api_root_url='{}/api/v1'.format(org_url),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': 'SSWS {}'.format(api_key),
            },
            timeout=10,
            json_encode_body=True,
        )


class UserFactorResource(Resource):
    actions = {
        'get': {'method': 'GET', 'url': 'users/{}/factors'},
        'issue': {'method': 'POST', 'url': 'users/{}/factors/{}/verify'},
        'verify': {'method': 'GET', 'url': 'users/{}/factors/{}/transactions/{}'}
    }
    actions.update(get_api_default_actions('factors'))


def decode_token(token):
    return jwt.decode(token, verify=False)
