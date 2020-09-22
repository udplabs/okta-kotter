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
    DB_CONNS = {}
    OKTA_SCOPES = os.getenv('OKTA_SCOPES').split(',')
    OKTA_ADMIN_SCOPES = os.getenv('OKTA_ADMIN_SCOPES').split(',')
    OKTA_O4O_SCOPES = os.getenv('OKTA_O4O_SCOPES').split(',')
    # NOTE: other .env settings are read into database, see util/settings.py


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True


class ProductionConfig(BaseConfig):
    pass

