from flask import current_app
from tinydb import TinyDB, Query, where


class Model(object):
    TYPE = ''

    def __init__(self):
        self.db = TinyDB(current_app.config['DB_PATH'])
        self.table = self.db.table(self.get_type())

    def get_type(self):
        return self.TYPE

    def all(self):
        results = []
        for row in self.table.all():
            row['id'] = row.eid
            results.append(row)
        return results

    def get(self, condition=None):
        if condition:
            if type(condition) == dict:
                # FIXME: can only filter on one key/value pair for condition
                records = Query()
                cond_key = list(condition.keys())[0]
                cond_val = list(condition.values())[0]
                results = self.table.search((records[cond_key]==cond_val))
            else:  # assume it's a doc ID
                results = [self.table.get(doc_id=condition)]
        else:
            results = self.table.all()
        updated_results = []
        for row in results:
            row['id'] = row.eid
            updated_results.append(row)
        return updated_results

    def add(self, data):
        self.table.insert(data)

    def update(self, data, condition=None):
        if condition:
            if type(condition) == dict:
                records = Query()
                cond_key = list(condition.keys())[0]
                cond_val = list(condition.values())[0]
                self.table.update(data, records[cond_key]==cond_val)
            else:  # it's a list of id(s)
                self.table.update(data, doc_ids=condition)
        else:
            self.table.update(data)

    def delete(self, key, value):
        self.table.remove(where(key) == value)
        # FIXME: below should work
        # self.table.remove(doc_ids=[key])


class Product(Model):
    TYPE = 'products'


class Order(Model):
    TYPE = 'orders'
