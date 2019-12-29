from datetime import datetime, timedelta

from flask import current_app
from tinydb import TinyDB, Query

# from .app import app
# from .util import groupsio_api_query

class Model(object):
    TYPE = ''

    def __init__(self):
        self.db = TinyDB(current_app.config['DB_PATH'])

    def get_type(self):
        return self.TYPE

    def all(self):
        Item = Query()
        results = self.db.search(Item.target == 'PUBLIC')
        return results


class Item(Model):
    # TODO: is this really used?
    TYPE = 'items'

