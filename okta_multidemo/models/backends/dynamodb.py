import os
import uuid

import boto3
from boto3.dynamodb.conditions import Attr, Key

from ..base import Model as BaseModel


def get_db():
    AWS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
    if AWS_KEY:
        db = boto3.resource('dynamodb')
    else:
        db = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
    return db


class Model(BaseModel):

    def __init__(self, db, tenant, table, table_prefix):
        self.db = db  # TODO: should this be a param, or just get_db here?
        self.tenant = tenant
        self.table = self.db.Table('{}{}'.format(table_prefix, table))

    def all_(self):
        data = self.table.scan()
        return data['Items']

    def all(self):
        response = self.table.query(
            IndexName='tenant',
            KeyConditionExpression=Key('tenant').eq(self.tenant),
            # FilterExpression=Attr('title').eq('Product 9')
        )
        result = response['Items']
        if result:
            if 'name' in result[0].keys():
                return sorted(result, key=lambda i: i['name'])
        return result

    def get(self, condition=None):
        if condition:
            if type(condition) == dict:
                # FIXME: can only filter on one key/value pair for condition?
                cond_key = list(condition.keys())[0]
                cond_val = list(condition.values())[0]
                resp = self.table.query(
                    IndexName='tenant',
                    KeyConditionExpression=Key('tenant').eq(self.tenant),
                    FilterExpression=Attr(cond_key).eq(str(cond_val))
                    # FIXME: ^^^ ugh, cast everything to str?
                )
            else:  # assume it's id
                # FIXME: filter by tenant
                resp = self.table.query(
                    IndexName='tenant',
                    KeyConditionExpression=Key('tenant').eq(self.tenant),
                    FilterExpression=Attr('id').eq(condition)  # FIXME: use PK
                )
            result = resp['Items']
        else:
            result = self.all()
        if result:
            if 'name' in result[0].keys():
                return sorted(result, key=lambda i: i['name'])
        return result

    def add(self, data):
        data['tenant'] = self.tenant
        data['id'] = uuid.uuid4().hex
        self.table.put_item(Item=data)

    def update(self, data, condition=None):
        # FIXME: filter by tenant
        update_exps = []
        exp_attrs = {}
        exp_attr_names = {}
        for ct, i in enumerate(data.keys()):
            attr = 'attr{}'.format(ct)
            val = 'val{}'.format(ct)
            update_exp = '#{} = :{}'.format(attr, val)
            update_exps.append(update_exp)
            exp_attrs[':{}'.format(val)] = data[i]
            exp_attr_names['#{}'.format(attr)] = i
        update_exps = ', '.join(update_exps)
        key_exp = {'id': str(condition[0])}  # FIXME ugh
        # FIXME: weirdly condition is a list of ID's,
        #   need to be able to support other conditions
        self.table.update_item(
            Key=key_exp,
            UpdateExpression='SET {}'.format(update_exps),
            ExpressionAttributeValues=exp_attrs,
            ExpressionAttributeNames=exp_attr_names,
            ReturnValues="UPDATED_NEW"
        )

    def delete(self, key, value):
        if key == 'id':
            # FIXME: filter by tenant
            self.table.delete_item(Key={'id': value})
        else:
            response = self.table.query(
                IndexName='tenant',
                KeyConditionExpression=Key('tenant').eq(self.tenant),
                FilterExpression=Attr(key).eq(value)
            )
            for i in response['Items']:
                self.table.delete_item(Key={'id': i['id']})

    def purge(self):
        items = self.all()
        for i in items:
            self.table.delete_item(Key={'id': i['id']})
