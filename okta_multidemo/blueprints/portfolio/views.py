from collections import Counter

from flask import session, render_template, Blueprint, redirect, url_for, request

from .util import get_api_client
from ..admin.util import auth_o4o
from ...util.settings import app_settings
from ...models import get_model

portfolio_blueprint = Blueprint('portfolio', 'portfolio', url_prefix='/portfolio')


@portfolio_blueprint.route('/', methods=('GET',))
@auth_o4o('portfolio.index')
def index(user_id=None):
    # TODO: use API rather than accessing models directly
    order = get_model('orders')
    orders = []
    images = {}
    for i in order.get({'userId': session['user_id']}):
        images[i['productTitle']] = i['productImage']
        # FIXME: ^^^ ugh kludgy way of getting images into page
        orders.append(i['productTitle'])
    # orders = [i['productTitle'] for i in order.get({'userId': session['user_id']})]
    order_list = list(zip(Counter(orders).keys(), Counter(orders).values()))
    # TODO: only return items with status "complete"?

    okta_api = get_api_client()
    grants = okta_api.grants.list(session['user_id'])
    # print(grants.body[0])

    return render_template(
        'blueprints/portfolio/index.html',
        orders=order_list,
        images=images,
        grants=grants.body,
        config=app_settings()
    )


@portfolio_blueprint.route('/revoke', methods=('GET',))
@auth_o4o('portfolio.revoke_consent')
def revoke_consent():
    """TODO: docstring."""
    grant_id = request.args.get('grant_id')
    okta_api = get_api_client()
    okta_api.grants.delete(session['user_id'], grant_id)
    return redirect(url_for('portfolio.index'))
