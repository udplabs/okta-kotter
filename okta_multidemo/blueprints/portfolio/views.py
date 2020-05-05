import json
from collections import Counter

import requests

from flask import session, render_template, Blueprint

from .util import authorize
from ...models import Order, Product

portfolio_blueprint = Blueprint('portfolio', 'portfolio', url_prefix='/portfolio')


@portfolio_blueprint.route('/', methods=('GET',))
@authorize()
def index(user_id=None):
    # TODO: use API rather than accessing models directly
    order = Order()
    product = Product()
    orders = []
    images = {}
    for i in order.get({'userId': session['user_id']}):
        print(i)
        images[i['productTitle']] = i['productImage']
        # FIXME: ^^^ ugh kludgy way of getting images into page
        orders.append(i['productTitle'])
    # orders = [i['productTitle'] for i in order.get({'userId': session['user_id']})]
    order_list = list(zip(Counter(orders).keys(), Counter(orders).values()))
    # TODO: only return items with status "complete"?
    return render_template(
        'blueprints/portfolio/index.html',
        orders=order_list,
        images=images
    )
