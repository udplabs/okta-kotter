import json

from flask import Blueprint, request, jsonify, session, current_app, Response
from tinydb import TinyDB, Query

from ..models import Item, Order
from .util import authorize

api_blueprint = Blueprint('api', 'api', url_prefix='/api')


@api_blueprint.route('/items', methods=['GET'])
@authorize(scopes=['items:read'])
def get_items():
    items = Item()
    data = items.all()
    return jsonify(data)


@api_blueprint.route('/orders', methods=['POST'])
@authorize(scopes=['items:read'])
def create_order():
    order = Order()
    data = json.loads(request.get_data())
    data['status'] = 'pending'
    result = order.add(data)
    resp = {'message': 'OK'}
    return jsonify(data)  # equivalent of Response(json.dumps(resp), 200)


@api_blueprint.route('/orders', methods=['GET'])
# @authorize(scopes=['orders:update'])
def get_orders():
    status = request.args.get('status')
    orders = Order()
    if status:
        data = orders.get({'status': status})
    else:
        data = orders.get()
    return jsonify(data)


@api_blueprint.route('/orders/<int:order_id>', methods=['PATCH'])
# @authorize(scopes=['orders:update'])
def update_order(order_id):
    order = Order()
    data = request.get_json()
    order.update(data)
    return jsonify([])  # TODO
