import json
import time

from flask import Blueprint, request, jsonify, session, current_app, Response
from tinydb import TinyDB, Query

from ..models import Product, Order
from .util import authorize, mfa

api_blueprint = Blueprint('api', 'api', url_prefix='/api')


@api_blueprint.route('/products', methods=['GET'])
@authorize(scopes=['products:read'])
def get_products(claims={}):
    products = Product()
    feature_access = claims.get('feature_access', [])
    if 'premium' in feature_access:
        data = products.all()
    else:
        data = products.get({'target': 'PUBLIC'})
    return jsonify(data)


@api_blueprint.route('/orders', methods=['POST'])
@authorize(scopes=['products:read'])
def create_order(claims={}):
    order = Order()
    data = json.loads(request.get_data())
    data['status'] = 'pending'
    result = order.add(data)
    resp = {'message': 'OK'}
    return jsonify(data)  # equivalent of Response(json.dumps(resp), 200)


@api_blueprint.route('/orders', methods=['GET'])
@authorize(scopes=['orders:update'])
def get_orders(claims={}):
    status = request.args.get('status')
    orders = Order()
    if status:
        data = orders.get({'status': status})
    else:
        data = orders.get()
    return jsonify(data)


@api_blueprint.route('/orders/<int:order_id>', methods=['PATCH'])
@authorize(scopes=['orders:update'])
@mfa()
def update_order(order_id, claims={}):
    data = json.loads(request.get_data())
    order_model = Order()
    product_model = Product()
    order = order_model.get(order_id)[0]
    product = product_model.get(order['itemId'])[0]
    product_model.update({'count': product['count']-1}, [order['itemId']])
    order_model.update(data, [order_id])
    return jsonify({'message': 'OK'})
