import json
import os

from pathlib import Path

import mistune
import jwt
import requests

from simple_rest_client.api import API
from simple_rest_client.resource import Resource

from tinydb import TinyDB


def init_db(path, theme_uri, app_url, items_img=None):
    try:
        os.remove(path)
    except OSError:
        pass
    db = TinyDB(path)
    table = db.table('products')
    path = Path(__file__).parent.absolute()

    if not theme_uri.startswith(app_url):
        resp = requests.get('{}/data.json'.format(theme_uri))
        data = resp.content
    else:
        # get local theme data from filesystem instead of remote URL
        theme = theme_uri.split('/')[-1]
        with open(os.path.join(
                path, '..', 'static/themes/{}/data.json'.format(theme)
        )) as file_:
            data = file_.read()
    products = json.loads(data)
    if items_img:
        img_path = '{}/img-items/'.format(theme_uri)
    else:
        img_path = '{}/static/img/items/'.format(app_url)

    product_map = {}
    for ct, i in enumerate(products):
        img = '{}{}'.format(img_path, i['image'])
        product_map[i['itemId']] = {
            'title': i['title'],
            'image': img
        }
        products[ct]['image'] = img
    table.insert_multiple(products)

    table = db.table('orders')
    with open(os.path.join(path, '..', 'conf/orders.json')) as file_:
        data = file_.read()
    orders = json.loads(data)
    for i in orders:
        try:
            i.update({
                'productTitle': product_map[str(i['itemId'])]['title'],
                'productImage': product_map[str(i['itemId'])]['image'],
            })
        except KeyError:
            # might not be available in product_map if order data is out of sync
            pass
    table.insert_multiple(orders)


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
    def __init__(self, org_url, api_key, api_type='api'):
        self.api = API(
            api_root_url='{}/{}/v1'.format(org_url, api_type),
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


def get_help_markdown(view_name, session, request):
    logged_in_ext = ''
    if session.get('username'):
        logged_in_ext = '-logged-in'
    path = Path(__file__).parent.absolute()
    file_not_found = False
    file_paths = [
        os.path.join(path, '..', 'help/{}{}.md'.format(view_name, logged_in_ext)),
        os.path.join(path, '..', 'help/{}.md'.format(view_name)),
        os.path.join(path, '..', 'help/{}.md'.format(request.endpoint)),
        os.path.join(path, '..', 'help/{}.md'.format(request.endpoint, logged_in_ext)),
    ]
    data = None
    for filepath in file_paths:
        file = Path(filepath)
        if file.exists():
            file.exists()
            with open(filepath) as file_:
                data = file_.read()
            break
    if not data:
        raise FileNotFoundError
    return mistune.markdown(data)
