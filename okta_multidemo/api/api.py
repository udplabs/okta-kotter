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
@authorize(scopes=['orders:write'])
def create_order():
    order = Order()
    data = json.loads(request.get_data())
    data['status'] = 'pending'
    result = order.add(data)
    resp = {'message': 'OK'}
    return jsonify(data)  # equivalent of Response(json.dumps(resp), 200)
