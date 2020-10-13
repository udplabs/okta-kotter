import os

import boto3

from dotenv import load_dotenv

from okta_multidemo.models import TENANT_MODELS

load_dotenv()
TABLE_PREFIX = os.getenv('DB_TABLE_PREFIX')
AWS_KEY = os.getenv('AWS_ACCESS_KEY_ID')


def init():
    if not AWS_KEY:
        dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
    else:
        dynamodb = boto3.resource('dynamodb')
    delete(dynamodb)
    for model in TENANT_MODELS:
        create(dynamodb, '{}{}'.format(TABLE_PREFIX, model))


def delete(dynamodb):
    table_iterator = dynamodb.tables.filter(
        ExclusiveStartTableName=TABLE_PREFIX
    )
    for i in table_iterator:
        i.delete()


def create(dynamodb, table_name):
    dynamodb.create_table(
        TableName=table_name,
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'tenant',
                'AttributeType': 'S'
            },
        ],
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'tenant',
                'KeySchema': [
                    {
                        'AttributeName': 'tenant',
                        'KeyType': 'HASH'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1,
                }
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )

if __name__ == '__main__':
    init()
