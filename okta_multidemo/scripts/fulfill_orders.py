import logging
import json
import os
from base64 import b64encode

import requests
from requests.auth import HTTPBasicAuth


from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.INFO)

OKTA_BASE_URL=os.getenv('OKTA_BASE_URL')
OKTA_ISSUER=os.getenv('OKTA_ISSUER')
OKTA_ADMIN_CLIENT_ID=os.getenv('OKTA_ADMIN_CLIENT_ID')
OKTA_ADMIN_CLIENT_SECRET=os.getenv('OKTA_ADMIN_CLIENT_SECRET')
OKTA_ADMIN_SCOPES=os.getenv('OKTA_ADMIN_SCOPES')
API_URL=os.getenv('API_URL')

# TODO: log activity to console
def update_orders():
    # get token using CC flow
    url = '{}/v1/token'.format(OKTA_ISSUER)
    auth = HTTPBasicAuth(OKTA_ADMIN_CLIENT_ID, OKTA_ADMIN_CLIENT_SECRET)
    headers = {
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
    }
    data = {
        'grant_type': 'client_credentials',
        'scope': 'orders:update'  # OKTA_ADMIN_SCOPES.split(','),
    }
    req = requests.post(
        url,
        headers=headers,
        data=data,
        auth=auth
    )
    authn_response = json.loads(req.content)
    access_token = authn_response['access_token']
    logging.info('Got access token: %s' % access_token)

    # get pending orders
    url = '{}/orders?status=pending'.format(API_URL)
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'authorization': 'Bearer {}'.format(access_token)
    }
    req = requests.get(
        url,
        headers=headers
    )
    orders = json.loads(req.content)
    logging.info('Got %d orders for processing.' % len(orders))

    # update pending orders
    for order in orders:
        url = '{}/orders/{}'.format(API_URL, order['id'])
        order.update({'status': 'complete'})
        # headers.update({'content-type': 'application/x-www-form-urlencoded'})
        req = requests.patch(
            url,
            headers=headers,
            data=json.dumps(order)
        )
    logging.info('Processed %d orders.' % len(orders))

if __name__ == '__main__':
    update_orders()

