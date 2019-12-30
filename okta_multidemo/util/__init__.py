import json
import os

import jwt

from simple_rest_client.api import API
from tinydb import TinyDB


def init_db(path, theme):
    try:
        os.remove(path)
    except OSError:
        pass
    db = TinyDB(path)
    table = db.table('items')
    # TODO: get relative to current module path
    with open('./okta_multidemo/conf/{}/data.json'.format(theme)) as file_:
        data = file_.read()
    items = json.loads(data)
    table.insert_multiple(items)


class APIClient(object):
    def __init__(self, api_url, access_token):
        self.api = API(
            api_root_url=api_url,
            headers={
                'Accept': 'application/json',
                'Content-type': 'application/json',
                'Authorization': 'Bearer {}'.format(access_token),
            },
            timeout=10,
            json_encode_body=True,
        )


def decode_token(token):
    return jwt.decode(token, verify=False)
