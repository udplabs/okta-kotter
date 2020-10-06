import json
import logging
import os
from pathlib import Path
from urllib.parse import urlparse

import requests
from requests.auth import HTTPBasicAuth
from flask import session, current_app, request


def get_theme_config(theme_uri, app_url):
    if not theme_uri.startswith(app_url):
        resp = requests.get('{}/config.json'.format(theme_uri))
        data = json.loads(resp.content)
        return data
    # get local theme from filesystem instead of remote URL
    theme = theme_uri.split('/')[-1]
    path = Path(__file__).parent.absolute()
    with open(os.path.join(
        path, '..', 'static/themes/{}/config.json'.format(theme)
    )) as file_:
        data = file_.read()
    return json.loads(data)


def is_true(var):
    if not os.getenv(var):
        return False
    return True if os.getenv(var).lower() == 'true' else False


def get_theme_uri(theme, app_url):
    if theme.startswith('http'):
        return theme
    else:
        return '{}/static/themes/{}'.format(app_url, theme)


def _get_local_settings():
    logging.info('Using local settings')
    app_url = os.getenv('APP_URL')
    theme = os.getenv('THEME', 'default')
    theme_uri = get_theme_uri(theme, app_url)

    theme_config = get_theme_config(theme_uri, app_url)
    settings = {
        'APP_URL': app_url,
        'API_URL': '{}/api'.format(app_url),
        'FF_DEVELOPER': is_true('FF_DEVELOPER'),
        'FF_DEVELOPER_CC_POLICY_ID': os.getenv('FF_DEVELOPER_CC_POLICY_ID'),
        'FF_DEVELOPER_PKCE_POLICY_ID': os.getenv('FF_DEVELOPER_PKCE_POLICY_ID'),
        'FF_PORTFOLIO': is_true('FF_PORTFOLIO'),
        'FF_PORTFOLIO_CLIENT_GROUP': os.getenv('FF_PORTFOLIO_CLIENT_GROUP'),
        'FF_EVENTS': is_true('FF_EVENTS'),
        'FF_EVENTS_HOOK_ID': os.getenv('FF_EVENTS_HOOK_ID'),
        'OKTA_BASE_URL': os.getenv('OKTA_BASE_URL'),
        'OKTA_API_KEY': os.getenv('OKTA_API_KEY'),
        'OKTA_CLIENT_ID': os.getenv('OKTA_CLIENT_ID'),
        'OKTA_CLIENT_SECRET': os.getenv('OKTA_CLIENT_SECRET'),
        'OKTA_ISSUER': os.getenv('OKTA_ISSUER'),
        'OKTA_AUDIENCE': os.getenv('OKTA_AUDIENCE'),
        'OKTA_GOOGLE_IDP': os.getenv('OKTA_GOOGLE_IDP'),
        'OKTA_FACEBOOK_IDP': os.getenv('OKTA_FACEBOOK_IDP'),
        'OKTA_SAML_IDP': os.getenv('OKTA_SAML_IDP'),
        'OKTA_ADMIN_CLIENT_ID': os.getenv('OKTA_ADMIN_CLIENT_ID'),
        'OKTA_IDP_REQUEST_CONTEXT': os.getenv('OKTA_IDP_REQUEST_CONTEXT'),
        'OKTA_RESOURCE_PREFIX': os.getenv('OKTA_RESOURCE_PREFIX', ''),
        'OKTA_SIW_PASSWORDLESS': is_true('OKTA_SIW_PASSWORDLESS'),
        'OKTA_SIW_ROUTER': is_true('OKTA_SIW_ROUTER'),
        'OKTA_SIW_REGISTRATION': is_true('OKTA_SIW_REGISTRATION'),
        'OKTA_SIW_REMEMBERME': is_true('OKTA_SIW_REMEMBERME'),
        'OKTA_SIW_MULTIOPTIONALFACTORENROLL': is_true('OKTA_SIW_MULTIOPTIONALFACTORENROLL'),
        'OKTA_SIW_SELFSERVICEUNLOCK': is_true('OKTA_SIW_SELFSERVICEUNLOCK'),
        'OKTA_SIW_SMSRECOVERY': is_true('OKTA_SIW_SMSRECOVERY'),
        'OKTA_SIW_CALLRECOVERY': is_true('OKTA_SIW_CALLRECOVERY'),
        'OKTA_SIW_USERNAMEPLACEHOLDER': os.getenv('OKTA_SIW_USERNAMEPLACEHOLDER'),
        'OKTA_SIW_PASSWORDPLACEHOLDER': os.getenv('OKTA_SIW_PASSWORDPLACEHOLDER'),
        'OKTA_SIW_USERNAMETOOLTIP': os.getenv('OKTA_SIW_USERNAMETOOLTIP'),
        'OKTA_SIW_PASSWORDTOOLTIP': os.getenv('OKTA_SIW_PASSWORDTOOLTIP'),
        'THEME': theme,
        'THEME_URI': theme_uri,
        'THEME_LABEL': theme_config['label'],
        'SITE_TITLE': theme_config['site-title'],
        'ITEMS_TITLE': theme_config['items-title'],
        'ITEMS_TITLE_LABEL': theme_config['items-title-label'],
        'ITEMS_ACTION_TITLE': theme_config['action-title'],
        'ITEMS_IMG': theme_config.get('img-items', False)  # whether items have custom images in img-items dir
    }
    return settings


def get_settings(env):
    if env == 'production':
        # get settings from UDP
        host_parts = urlparse(request.url).hostname.split('.')
        subdomain = host_parts[0]
        app_name = host_parts[1]

        # get access token from UDP using client credentials flow
        url = '{}/v1/token'.format(os.getenv('UDP_ISSUER'))
        auth = HTTPBasicAuth(
            os.getenv('UDP_CLIENT_ID'), os.getenv('UDP_CLIENT_SECRET'))
        headers = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
        }
        data = {
            'grant_type': 'client_credentials',
            'scope': 'secrets:read',
        }
        req = requests.post(url, headers=headers, data=data, auth=auth)
        authn_response = json.loads(req.content)
        access_token = authn_response['access_token']

        # get settings from UDP using access token
        url = '{}/api/configs/{}/{}'.format(
            os.getenv('UDP_CONFIG_URL'),
            subdomain,
            app_name
        )
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'authorization': 'Bearer {}'.format(access_token)
        }
        try:
            req = requests.get(url, headers=headers)
            settings = json.loads(req.content)['settings']
            settings_dict = {}
            for i in settings:
                key = i.upper()
                settings_dict[key] = settings[i]
            return settings_dict
        except Exception as e:
            logging.warning('Unable to retrieve remote UDP config')
            logging.exception('{}: {}'.format(type(e), str(e)))
        return _get_local_settings()
    else:  # 'development' - get settings from local env file
        return _get_local_settings()


def get_db():
    subdomain = session.get('subdomain')
    if not subdomain:
        subdomain = urlparse(request.url).hostname.split('.')[0]
    # FIXME: below is specific to ngrok implementation for Event hook
    if subdomain == 'tunnel':
        subdomain = 'localhost'
    db = current_app.config['DB_CONNS'][subdomain]
    return db


def app_settings():
    db = get_db()
    table = db.table('settings')
    results = table.all()
    settings = {}
    for i in results:
        settings[i['setting']] = i['value']
    settings.update(dict(current_app.config))
    return settings
