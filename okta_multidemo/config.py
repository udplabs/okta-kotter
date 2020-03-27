import json
import os

from pathlib import Path

import requests

from dotenv import load_dotenv
load_dotenv()


def get_theme_config(theme_uri, app_url):
    if not theme_uri.startswith(app_url):
        resp = requests.get('{}/config.json'.format(theme_uri))
        data = json.loads(resp.content)
        return data
    # get local theme from filesystem instead of remote URL
    theme = theme_uri.split('/')[-1]
    path = Path(__file__).parent.absolute()
    with open(os.path.join(
            path, 'static/themes/{}/config.json'.format(theme)
        )) as file_:
        data = file_.read()
    return json.loads(data)

class BaseConfig(object):
    DEBUG = False
    TESTING = False
    SITE_NAME = ''
    SECRET_KEY = os.getenv('SECRET_KEY')
    APP_URL=os.getenv('APP_URL')
    DB_PATH=os.getenv('DB_PATH')
    API_URL=os.getenv('API_URL')
    PERSIST_DB=True if os.getenv('PERSIST_DB') == 'true' else False

    FF_DEVELOPER=True if os.getenv('FF_DEVELOPER') == 'true' else False
    FF_DEVELOPER_CC_POLICY_ID=os.getenv('FF_DEVELOPER_CC_POLICY_ID')

    OKTA_BASE_URL=os.getenv('OKTA_BASE_URL')
    OKTA_API_KEY=os.getenv('OKTA_API_KEY')
    OKTA_CLIENT_ID=os.getenv('OKTA_CLIENT_ID')
    OKTA_CLIENT_SECRET=os.getenv('OKTA_CLIENT_SECRET')
    OKTA_ISSUER=os.getenv('OKTA_ISSUER')
    OKTA_AUDIENCE=os.getenv('OKTA_AUDIENCE')
    OKTA_GOOGLE_IDP=os.getenv('OKTA_GOOGLE_IDP')
    OKTA_FACEBOOK_IDP=os.getenv('OKTA_FACEBOOK_IDP')
    OKTA_SAML_IDP=os.getenv('OKTA_SAML_IDP')
    OKTA_SCOPES=os.getenv('OKTA_SCOPES').split(',')
    OKTA_ADMIN_SCOPES=os.getenv('OKTA_ADMIN_SCOPES').split(',')
    OKTA_ADMIN_CLIENT_ID=os.getenv('OKTA_ADMIN_CLIENT_ID')
    OKTA_IDP_REQUEST_CONTEXT=os.getenv('OKTA_IDP_REQUEST_CONTEXT')

    THEME_URI=os.getenv('THEME_URI', 'http://localhost:5000/static/themes/default')
    theme_config = get_theme_config(THEME_URI, APP_URL)
    THEME_LABEL = theme_config['label']
    SITE_TITLE = theme_config['site-title']
    ITEMS_TITLE = theme_config['items-title']
    ITEMS_TITLE_LABEL = theme_config['items-title-label']
    ITEMS_PATH = '/{}'.format(theme_config['items-title-label'])
    ITEMS_ACTION_TITLE = theme_config['action-title']
    ITEMS_IMG = theme_config.get('img-items', False)  # whether items have custom images in img-items dir


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True


class ProductionConfig(BaseConfig):
    pass
