from datetime import datetime, timedelta

from flask import current_app
from tinydb import TinyDB, Query

# from .app import app
# from .util import groupsio_api_query

class Model(object):
    TYPE = ''

    def __init__(self):
        self.db = TinyDB(current_app.config['DB_PATH'])
        self.table = self.db.table(self.get_type())

    def get_type(self):
        return self.TYPE

    def all(self):
        # records = Query()
        # results = self.db.search(records.target == 'PUBLIC')
        results = self.table.all()
        return results

    def add(self, data):
        self.table.insert(data)


# TODO: are the subclasses really necessary?
class Item(Model):
    TYPE = 'items'


class Order(Model):
    TYPE = 'orders'
