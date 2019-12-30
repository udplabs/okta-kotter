from flask import url_for

def get_widget_config(app_conf, type_=None):
    widget_conf = {
        'baseUrl': app_conf['OKTA_BASE_URL'],
        'clientId': app_conf['OKTA_CLIENT_ID'],
        'logo': '/static/img/themes/{}/icon.png'.format(app_conf['THEME_LABEL']),
        'language': 'en',
        'i18n': {
            'en': {
                'primaryauth.title': 'Sign in to {}'.format(app_conf['SITE_TITLE'])
            }
        },
        'authParams': {
            'issuer': app_conf['OKTA_ISSUER'],
            'scopes': app_conf['OKTA_SCOPES'],
        }
    }

    if type_ in ['implicit', 'social']:
        widget_conf['redirectUri'] = '{}/implicit/callback'.format(
            app_conf['OKTA_AUDIENCE'])
        widget_conf['authParams']['responseType'] = ['token', 'id_token']
        if type_ == 'social':
            widget_conf['idps'] = [
                {'type': 'GOOGLE', 'id': app_conf['OKTA_GOOGLE_IDP']},
                {'type': 'FACEBOOK', 'id': app_conf['OKTA_FACEBOOK_IDP']},
                {'id': '0oa66b17m0XBRYUyp356', 'text': 'Login with SAML IdP', 'className': '' }
            ]
            widget_conf['authParams']['display'] = 'popup'
    else:
        widget_conf['redirectUri'] = '{}{}/authorized'.format(
            app_conf['OKTA_AUDIENCE'], url_for('okta.login')
        )
        widget_conf['authParams']['responseType'] = ['code']
    return widget_conf
