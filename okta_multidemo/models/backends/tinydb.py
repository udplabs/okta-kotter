from tinydb import TinyDB, Query, where

from ..base import Model as BaseModel


def get_db(db_path):
    db = TinyDB(db_path)
    return db


class Model(BaseModel):

    def __init__(self, db, tenant, table):
        self.db = db
        self.tenant = tenant
        self.table = self.db.table(table)

    def all_(self):
        results = []
        for row in self.table.all():
            row['id'] = row.doc_id
            results.append(row)
        return results

    def all(self):
        results = self.table.search((where('tenant') == self.tenant))
        if results:
            if 'name' in results[0].keys():
                results = sorted(results, key=lambda i: i['name'])
        return results

    def get(self, condition=None):
        if condition:
            if type(condition) == dict:
                # FIXME: can only filter on one key/value pair for condition
                records = Query()
                cond_key = list(condition.keys())[0]
                cond_val = list(condition.values())[0]
                results = self.table.search(
                    (where('tenant') == self.tenant) & (records[cond_key]==cond_val)
                )
            else:  # assume it's a doc ID
                # FIXME: filter by tenant
                results = [self.table.get(doc_id=int(condition))]
                # TODO: stop useing doc_ids, and just key on 'id'
        else:
            results = self.all()
        if results:
            if 'name' in results[0].keys():
                results = sorted(results, key=lambda i: i['name'])
        return results

    def add(self, data):
        data['tenant'] = self.tenant
        id_ = self.table.insert(data)
        self.update({'id': id_}, [id_])

    def update(self, data, condition=None):
        # FIXME: filter by tenant
        if condition:
            if type(condition) == dict:
                records = Query()
                cond_key = list(condition.keys())[0]
                cond_val = list(condition.values())[0]
                self.table.update(data, records[cond_key]==cond_val)
            else:  # it's a list of id(s)
                self.table.update(data, doc_ids=[int(i) for i in condition])
                # TODO: stop using doc_ids, and just key on 'id'
        else:
            self.table.update(data)

    def delete(self, key, value):
        # FIXME: filter by tenant
        self.table.remove(where(key) == value)
        # FIXME: below should work
        # self.table.remove(doc_ids=[key])

    def purge(self):
        self.table.remove(where('tenant') == self.tenant)
