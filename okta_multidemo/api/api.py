import json

from flask import Blueprint, request, jsonify, session, current_app
from tinydb import TinyDB, Query

from ..models import Item
from .util import authorization_required

api_blueprint = Blueprint('api', 'api', url_prefix='/api')


@api_blueprint.route('/items', methods=['GET'])
@authorization_required(scopes=['items:read'])
def api_items_get():
    # validate_access_token(token)
    items = Item()
    data = items.all()
    return jsonify(data)


@api_blueprint.route('/orders', methods=['POST'])
def create_order():
    req_data = request.get_data()
    print('############')
    print(json.loads(req_data))
    # TODO: get user ID from ID token in session to add to record in DB
    return jsonify([])
    # if request.method == 'POST':
    #     # add an item to DB
    #     return jsonify({'message': 'OK'})
