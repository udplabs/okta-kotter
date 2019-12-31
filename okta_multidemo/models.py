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

    def get(self, condition=None):
        print('#########', condition)
        if condition:
            records = Query()
            cond_key = list(condition.keys())[0]
            cond_val = list(condition.values())[0]
            results = self.table.search(records[cond_key]==cond_val)
        else:
            results = self.table.all()
        return results

    def add(self, data):
        self.table.insert(data)

    def update(self, data, condition=None):
        if condition:
            records = Query()
            cond_key = list(condition.keys())[0]
            cond_val = list(condition.values())[0]
            self.table.update(data, records[cond_key]==cond_val)
        else:
            self.table.update(data)


# TODO: are the subclasses really necessary?
class Item(Model):
    TYPE = 'items'


class Order(Model):
    TYPE = 'orders'
