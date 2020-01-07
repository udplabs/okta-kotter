import json
import time

from flask import Blueprint, request, jsonify, session, current_app, Response
from tinydb import TinyDB, Query

from ..models import Item, Order
from .util import authorize, mfa

api_blueprint = Blueprint('api', 'api', url_prefix='/api')


@api_blueprint.route('/items', methods=['GET'])
@authorize(scopes=['items:read'])
def get_items(claims={}):
    items = Item()
    feature_access = claims.get('feature_access', [])
    if 'premium' in feature_access:
        data = items.all()
    else:
        data = items.get({'target': 'PUBLIC'})
    return jsonify(data)


@api_blueprint.route('/orders', methods=['POST'])
@authorize(scopes=['items:read'])
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
    item_model = Item()
    order = order_model.get(order_id)[0]
    item = item_model.get(order['itemId'])[0]
    item_model.update({'count': item['count']-1}, [order['itemId']])
    order_model.update(data, [order_id])
    return jsonify({'message': 'OK'})
