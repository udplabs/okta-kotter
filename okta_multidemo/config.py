import json
import os

from dotenv import load_dotenv
load_dotenv()


def get_theme_config(theme):
    # TODO: get relative to current module path
    with open('./okta_multidemo/conf/{}/config.json'.format(theme)) as file_:
        data = file_.read()
    return json.loads(data)

class BaseConfig(object):
    DEBUG = False
    TESTING = False
    SITE_NAME = ''
    DB_PATH='/tmp/okta-demo-db.json'
    API_URL='http://localhost:5000/api'
    SECRET_KEY = os.getenv('SECRET_KEY')

    OKTA_BASE_URL=os.getenv('OKTA_BASE_URL')
    OKTA_CLIENT_ID=os.getenv('OKTA_CLIENT_ID')
    OKTA_CLIENT_SECRET=os.getenv('OKTA_CLIENT_SECRET')
    OKTA_ISSUER=os.getenv('OKTA_ISSUER')
    OKTA_AUDIENCE=os.getenv('OKTA_AUDIENCE')
    OKTA_GOOGLE_IDP=os.getenv('OKTA_GOOGLE_IDP')
    OKTA_FACEBOOK_IDP=os.getenv('OKTA_FACEBOOK_IDP')
    OKTA_SCOPES=os.getenv('OKTA_SCOPES').split(',')

    theme=os.getenv('THEME', 'default')
    theme_config = get_theme_config(theme)
    THEME_LABEL = theme_config['label']
    SITE_TITLE = theme_config['site-title']
    ITEMS_TITLE = theme_config['items-title']
    ITEMS_TITLE_LABEL = theme_config['items-title-label']
    ITEMS_PATH = '/{}'.format(theme_config['items-title-label'])
    ITEMS_ACTION_TITLE = theme_config['action-title']


class DevelopmentConfig(BaseConfig):
    SECRET_KEY = os.getenv('SECRET_KEY')
    SITE_NAME = os.getenv('SITE_NAME')
    HOME_HTML = os.getenv('HOME_HTML')
    DEBUG = True
    TESTING = True


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True


class ProductionConfig(BaseConfig):
    SECRET_KEY = os.getenv('SECRET_KEY')
    SITE_NAME = os.getenv('SITE_NAME')
    HOME_HTML = os.getenv('HOME_HTML')
    GROUP_ID="1"
