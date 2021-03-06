import json
import logging
import os
from pathlib import Path
from urllib.parse import urlparse

import requests
from requests.auth import HTTPBasicAuth
from flask import current_app, request, session
from werkzeug.exceptions import NotFound, InternalServerError

from ..models import get_model
from ..cache import cache


BOOLS = [
    'FF_DEVELOPER',
    'FF_PORTFOLIO',
    'FF_EVENTS',
    'OKTA_SIW_PASSWORDLESS',
    'OKTA_SIW_ROUTER',
    'OKTA_SIW_REGISTRATION',
    'OKTA_SIW_REMEMBERME',
    'OKTA_SIW_MULTIOPTIONALFACTORENROLL',
    'OKTA_SIW_SELFSERVICEUNLOCK',
    'OKTA_SIW_SMSRECOVERY',
    'OKTA_SIW_CALLRECOVERY',
]
UDP_ACCESS_TOKEN_EXPIRATION = 1800  # using 30m instead 60m for now


@cache.memoize()
def get_theme_config(theme, theme_uri, app_url):
    if theme.startswith('http'):
        resp = requests.get('{}/config.json'.format(theme_uri))
        data = json.loads(resp.content)
        return data
    # get local theme from filesystem instead of remote URL
    path = Path(__file__).parent.absolute()
    with open(os.path.join(
        path, '..', 'static/themes/{}/config.json'.format(theme)
    )) as file_:
        data = file_.read()
    return json.loads(data)


def is_true(var):
    # if not os.getenv(var):
    #     return False
    # return True if os.getenv(var).lower() == 'true' else False
    if var is True:
        return True
    return True if str(var).lower() == 'true' else False


def get_theme_uri(theme, static_url):
    if theme.startswith('http'):
        return theme
    else:
        return '{}/themes/{}'.format(static_url, theme)


def _get_local_settings():
    app_url = os.getenv('APP_URL')
    theme = os.getenv('THEME', 'default')
    static_url = os.getenv('AWS_CLOUDFRONT_URL') if os.getenv('FLASK_ENV') == 'production' \
        else '{}/static'.format(app_url)  # normally this func used in dev not prod
    theme_uri = get_theme_uri(theme, static_url)
    theme_config = get_theme_config(theme, theme_uri, app_url)
    settings = {
        'APP_URL': app_url,
        'API_URL': '{}/api'.format(app_url),
        'FF_DEVELOPER': is_true(os.getenv('FF_DEVELOPER')),
        'FF_DEVELOPER_CC_POLICY_ID': os.getenv('FF_DEVELOPER_CC_POLICY_ID'),
        'FF_DEVELOPER_PKCE_POLICY_ID': os.getenv('FF_DEVELOPER_PKCE_POLICY_ID'),
        'FF_PORTFOLIO': is_true(os.getenv('FF_PORTFOLIO')),
        'FF_PORTFOLIO_CLIENT_GROUP': os.getenv('FF_PORTFOLIO_CLIENT_GROUP'),
        'FF_EVENTS': is_true(os.getenv('FF_EVENTS')),
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
        'OKTA_SIW_PASSWORDLESS': is_true(os.getenv('OKTA_SIW_PASSWORDLESS')),
        'OKTA_SIW_ROUTER': is_true(os.getenv('OKTA_SIW_ROUTER')),
        'OKTA_SIW_REGISTRATION': is_true(os.getenv('OKTA_SIW_REGISTRATION')),
        'OKTA_SIW_REMEMBERME': is_true(os.getenv('OKTA_SIW_REMEMBERME')),
        'OKTA_SIW_MULTIOPTIONALFACTORENROLL': is_true(os.getenv('OKTA_SIW_MULTIOPTIONALFACTORENROLL')),
        'OKTA_SIW_SELFSERVICEUNLOCK': is_true(os.getenv('OKTA_SIW_SELFSERVICEUNLOCK')),
        'OKTA_SIW_SMSRECOVERY': is_true(os.getenv('OKTA_SIW_SMSRECOVERY')),
        'OKTA_SIW_CALLRECOVERY': is_true(os.getenv('OKTA_SIW_CALLRECOVERY')),
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
        'ITEMS_IMG': theme_config.get('img-items', False),  # whether items have custom images in img-items dir
        'STATIC_URL': static_url
    }
    return settings


@cache.cached(UDP_ACCESS_TOKEN_EXPIRATION)
def _get_access_token():
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
    return access_token


def get_settings(env):
    if env == 'production':
        # return _get_local_settings()  # local debugging
        # get settings from UDP
        host_parts = urlparse(request.url).hostname.split('.')
        subdomain = host_parts[0]
        app_name = host_parts[1]
        access_token = _get_access_token()

        # get settings from UDP using access token
        url = '{}/api/configs/{}/{}'.format(
            os.getenv('UDP_CONFIG_URL'),
            subdomain,
            app_name
        )
        logging.info('Getting settings from {}'.format(url))
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'authorization': 'Bearer {}'.format(access_token)
        }
        req = requests.get(url, headers=headers)
        if req.status_code != 200:
            if (req.status_code == 404):
                logging.warning('404 - no configuration for {}.{}?'.format(
                    subdomain, app_name))
                session.clear()
                raise NotFound
            else:
                logging.error('{} - API error'.format(req.status_code))
                raise InternalServerError  # TODO: better error handling
        resp = json.loads(req.content)
        try:
            settings = resp['settings']
            settings_dict = {}
            for i in settings:
                key = i.upper()
                if key in BOOLS:
                    settings_dict[key] = is_true(settings[i])
                else:
                    settings_dict[key] = settings[i]
            redir_url = urlparse(resp['redirect_uri'])
            app_url = '{}://{}'.format(redir_url.scheme, redir_url.netloc)
            theme = settings_dict['THEME']
            theme_uri = get_theme_uri(theme, os.getenv('AWS_CLOUDFRONT_URL'))
            theme_config = get_theme_config(theme, theme_uri, app_url)
            settings_dict.update({
                'OKTA_CLIENT_ID': resp['client_id'],
                'OKTA_CLIENT_SECRET': resp['client_secret'],
                'OKTA_ISSUER': resp['issuer'],
                'OKTA_BASE_URL': resp['okta_org_name'],
                'APP_URL': app_url,
                'API_URL': '{}/api'.format(app_url),
                'THEME': theme,
                'THEME_URI': theme_uri,
                'THEME_LABEL': theme_config['label'],
                'SITE_TITLE': theme_config['site-title'],
                'ITEMS_TITLE': theme_config['items-title'],
                'ITEMS_TITLE_LABEL': theme_config['items-title-label'],
                'ITEMS_ACTION_TITLE': theme_config['action-title'],
                'ITEMS_IMG': theme_config.get('img-items', False),
                'STATIC_URL': os.getenv('AWS_CLOUDFRONT_URL'),
                'OKTA_RESOURCE_PREFIX': os.getenv('OKTA_RESOURCE_PREFIX', ''),
            })
            return settings_dict
        except Exception as e:
            logging.warning('Unable to retrieve remote UDP config')
            logging.exception('{}: {}'.format(type(e), str(e)))
    else:
        logging.info('Using local settings')
    return _get_local_settings()


def app_settings(subdomain=None):
    settings = {}
    if session:
        for i in session:
            if i.startswith('__'):
                settings[i[2:]] = session[i]
    else:
        # for external clients with no session
        subdomain = urlparse(request.url).hostname.split('.')[0]
        tenant = get_model('tenants', subdomain)
        settings = tenant.get({'name': subdomain})[0]
    settings.update(dict(current_app.config))
    return settings
