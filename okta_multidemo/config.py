import os

from pathlib import Path


from dotenv import load_dotenv
# TODO: is OKTA_ALT_ENV used anymore? if not, remove below
alt_env = os.getenv('OKTA_ALT_ENV', None)
if alt_env:
    env_path = Path('.') / alt_env
    load_dotenv(dotenv_path=env_path, override=True)
else:
    load_dotenv()


class BaseConfig(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    DB_PATH = os.getenv('DB_PATH')
    OKTA_SCOPES = os.getenv('OKTA_SCOPES').split(',')
    OKTA_ADMIN_SCOPES = os.getenv('OKTA_ADMIN_SCOPES').split(',')
    OKTA_O4O_SCOPES = os.getenv('OKTA_O4O_SCOPES').split(',')
    UDP_CONFIG_URL = os.getenv('UDP_CONFIG_URL')
    UDP_ISSUER = os.getenv('UDP_ISSUER')
    UDP_CLIENT_ID = os.getenv('UDP_CLIENT_ID')
    UDP_CLIENT_SECRET = os.getenv('UDP_CLIENT_SECRET')
    DB_TABLE_PREFIX = os.getenv('DB_TABLE_PREFIX')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
    OKTA_RESOURCE_PREFIX = os.getenv('OKTA_RESOURCE_PREFIX')
    # NOTE: other .env settings are read into database, see util/settings.py


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True


class ProductionConfig(BaseConfig):
    pass

