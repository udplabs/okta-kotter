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


def is_true(var):
    if not os.getenv(var):
        return False
    return True if os.getenv(var).lower() == 'true' else False


class BaseConfig(object):
    DEBUG = False
    TESTING = False
    SITE_NAME = ''
    SECRET_KEY = os.getenv('SECRET_KEY')
    APP_URL=os.getenv('APP_URL')
    DB_PATH=os.getenv('DB_PATH')
    API_URL=os.getenv('API_URL')
    PERSIST_DB=is_true('PERSIST_DB')

    FF_DEVELOPER=is_true('FF_DEVELOPER')
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

    # START widget config
    OKTA_PASSWORDLESS=is_true('OKTA_PASSWORDLESS')
    OKTA_ROUTER=is_true('OKTA_ROUTER')
    OKTA_REGISTRATION=is_true('OKTA_REGISTRATION')
    OKTA_REMEMBERME=is_true('OKTA_REMEMBERME')
    OKTA_MULTIOPTIONALFACTORENROLL=is_true('OKTA_MULTIOPTIONALFACTORENROLL')
    OKTA_SELFSERVICEUNLOCK=is_true('OKTA_SELFSERVICEUNLOCK')
    OKTA_SMSRECOVERY=is_true('OKTA_SMSRECOVERY')
    OKTA_CALLRECOVERY=is_true('OKTA_CALLRECOVERY')
    OKTA_USERNAMEPLACEHOLDER=os.getenv('OKTA_USERNAMEPLACEHOLDER')
    OKTA_PASSWORDPLACEHOLDER=os.getenv('OKTA_PASSWORDPLACEHOLDER')
    OKTA_USERNAMETOOLTIP=os.getenv('OKTA_USERNAMETOOLTIP')
    OKTA_PASSWORDTOOLTIP=os.getenv('OKTA_PASSWORDTOOLTIP')
    # END widget config

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
