import json
from urllib.parse import urlparse

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from werkzeug.exceptions import Forbidden
import simplejson

from ...models import get_model
from .util import authorize, mfa, validate_access_token, get_token_from_header

api_blueprint = Blueprint('api', 'api', url_prefix='/api')


@api_blueprint.route('/products', methods=['GET'])
@authorize(scopes=['products:read'])
def get_products(claims={}):
    products = get_model('products')
    feature_access = claims.get('feature_access', [])
    if 'premium' in feature_access:
        data = products.all()
    else:
        data = products.get({'target': 'PUBLIC'})
    # return jsonify(data)
    return simplejson.dumps(data, use_decimal=True)


@api_blueprint.route('/orders', methods=['POST'])
@authorize(scopes=['orders:create'])
def create_order(claims={}):
    order = get_model('orders')
    prod_obj = get_model('products')
    data = json.loads(request.get_data())
    product = prod_obj.get({'itemId': data['itemId']})[0]
    data['status'] = 'pending'
    data['productTitle'] = product['name']
    data['productImage'] = product['image']
    order.add(data)
    return jsonify(data)  # equivalent of Response(json.dumps(resp), 200)


@api_blueprint.route('/orders', methods=['GET'])
@authorize(scopes=['orders:update'])
def get_orders(claims={}):
    status = request.args.get('status')
    orders = get_model('orders')
    if status:
        data = orders.get({'status': status})
    else:
        data = orders.all()
    return jsonify(data)


# NOTE: this endpoint is used by external applications only;
#   the intention is to require consent for the scope
@api_blueprint.route('/orders/<user_id>', methods=['GET', 'POST'])
@cross_origin()  # NOTE: the idea here would be to allow requests from registered clients; i.e. whitelist their domains
def get_user_orders(user_id, claims={}):
    # validating token without decorator because of user_id
    subdomain = urlparse(request.url).hostname.split('.')[0]
    scopes = ['orders:read:user']
    token = get_token_from_header()
    tenant = get_model('tenants')
    config = tenant.get({'name': subdomain})[0]
    try:
        validate_access_token(token, scopes, config, user_id)
    except AssertionError:
        raise Forbidden
    order = get_model('orders', subdomain)
    data = order.get({'userId': user_id})
    # TODO: only return items with status "complete"?
    return jsonify(data)


@api_blueprint.route('/orders/<order_id>', methods=['PATCH'])
@authorize(scopes=['orders:update'])
@mfa()
def update_order(order_id, claims={}):
    data = json.loads(request.get_data())
    order_model = get_model('orders')
    product_model = get_model('products')
    order = order_model.get(order_id)[0]
    product = product_model.get({'itemId': order['itemId']})[0]
    product_model.update({'count': product['count']-1}, [order['itemId']])
    order_model.update(data, [order_id])
    return jsonify({'message': 'OK'})

