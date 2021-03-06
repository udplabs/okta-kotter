import json
import logging
import os

from pathlib import Path

import jwt
import requests

from flask import session

from simple_rest_client.api import API
from simple_rest_client.resource import Resource

from .settings import get_settings
from ..models import get_model  # Setting, Product, Order, Tenant
from ..util.help import load_help


def _init_help():
    # used in dev env only
    parent_path = Path(__file__).parent.absolute()
    ct = load_help(parent_path, '/static')
    logging.debug('{} help templates generated.'.format(ct))


def init_settings(env):
    '''
    Get settings from either UDP or local env and assign them to session vars.
    '''
    settings = get_settings(env)
    for i in settings.keys():
        (session['__{}'.format(i)]) = settings[i]
    if env == 'development':
        _init_help()


def init_db(env, tenant):
    settings = get_settings(env)
    session['db_loaded'] = True
    m_tenant = get_model('tenants')
    existing_tenant = m_tenant.get({'name': tenant})
    if existing_tenant:
        return
    else:
        m_tenant.add({
            'name': tenant,
            'OKTA_ISSUER': settings['OKTA_ISSUER'],
            'OKTA_AUDIENCE': settings['OKTA_AUDIENCE'],
        })

    theme_uri = settings['THEME_URI']
    app_url = settings['APP_URL']
    items_img = settings['ITEMS_IMG']
    static_url = settings['STATIC_URL']

    # populate DB with sample product data
    m_product = get_model('products')
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
        img_path = '{}/img/items/'.format(static_url)

    product_map = {}
    for ct, i in enumerate(products):
        img = '{}{}'.format(img_path, i['image'])
        product_map[i['itemId']] = {
            'name': i['name'],
            'image': img,
        }
        products[ct]['image'] = img
        products[ct]['tenant'] = tenant
    for i in products:
        m_product.add(i)

    # populate DB with sample orders data
    m_order = get_model('orders')
    with open(os.path.join(path, '..', 'conf/orders.json')) as file_:
        data = file_.read()
    orders = json.loads(data)
    for i in orders:
        i['tenant'] = tenant
        try:
            i.update({
                'productTitle': product_map[str(i['itemId'])]['name'],
                'productImage': product_map[str(i['itemId'])]['image'],
            })
        except KeyError:
            # might not be available in product_map if order data is out of sync
            pass
    for i in orders:
        m_order.add(i)


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


def set_session_vars(session, id_token):
    id_decoded = decode_token(id_token)
    session['username'] = id_decoded['email']
    session['name'] = id_decoded['name']
    session['user_id'] = id_decoded['sub']
    session['is_admin'] = False
    for i in id_decoded.get('groups', []):
        if i.startswith('Admin'):
            session['is_admin'] = True
            break
