from werkzeug.exceptions import Unauthorized
from flask import Blueprint, request, redirect, session, url_for, jsonify, current_app
from requests_oauthlib import OAuth2Session

from ...util.settings import app_settings
from ...util import set_session_vars

auth_blueprint = Blueprint('auth', 'auth', url_prefix='/authorization-code')


@auth_blueprint.route('/')
def login():
    settings = app_settings()
    auth_conf = request.args.get('conf', 'okta')
    view = request.args.get('view', 'index')
    authn_url = '{}/v1/authorize'.format(settings['OKTA_ISSUER'])
    if auth_conf == 'okta-admin':
        scopes = current_app.config['OKTA_ADMIN_SCOPES']
    elif auth_conf == 'okta-o4o':
        scopes = current_app.config['OKTA_O4O_SCOPES']
        authn_url = '{}/oauth2/v1/authorize'.format(settings['OKTA_BASE_URL'])
    else:
        scopes = current_app.config['OKTA_SCOPES']
    oauth = OAuth2Session(
        settings['OKTA_CLIENT_ID'],
        redirect_uri='{}{}'.format(
            settings['APP_URL'], url_for('auth.callback')),
        scope=scopes
    )
    authorization_url, state = oauth.authorization_url(authn_url)
    session['oauth_state'] = state
    session['view'] = view
    session['auth_conf'] = auth_conf
    return redirect(authorization_url)


@auth_blueprint.route('/callback')
def callback():
    if request.args.get('iss'):
        # TODO: this is for IdP disco - probably should validate the value in 'iss'
        # See https://openid.net/specs/openid-connect-core-1_0.html#ThirdPartyInitiatedLogin
        return redirect(url_for('auth.login'))
    settings = app_settings()
    auth_conf = session.pop('auth_conf', 'okta')
    view = session.pop('view', 'index')
    if auth_conf == 'okta-o4o':
        token_url = '{}/oauth2/v1/token'.format(settings['OKTA_BASE_URL'])
    else:
        token_url = '{}/v1/token'.format(settings['OKTA_ISSUER'])
    oauth = OAuth2Session(
        settings['OKTA_CLIENT_ID'],
        state=session.get('oauth_state', None),
        redirect_uri='{}{}'.format(
            settings['APP_URL'], url_for('auth.callback'))
    )
    token = oauth.fetch_token(
        token_url,
        client_secret=settings['OKTA_CLIENT_SECRET'],
        authorization_response=request.url,
    )
    # TODO: does the above ever return anything but a token? error out?
    if not token:
        raise Unauthorized
    access_token = token['access_token']
    resp = redirect(url_for(view))
    if auth_conf == 'okta-o4o':
        resp.set_cookie('o4o_token', access_token)
    else:
        id_token = token['id_token']
        set_session_vars(session, id_token)
        resp.set_cookie('access_token', access_token)
        resp.set_cookie('id_token', id_token)
    return resp


@auth_blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    settings = app_settings()
    id_token = request.cookies.get('id_token')
    logout_url = '{}/v1/logout?id_token_hint={}&post_logout_redirect_uri={}'.format(
        settings['OKTA_ISSUER'],
        id_token,
        settings['APP_URL']
    )
    resp = redirect(logout_url)
    # resp = make_response(redirect(url_for('index')))
    # ^^^ use this instead to avoid killing Okta session
    resp.set_cookie('access_token', '', expires=0)
    resp.set_cookie('id_token', '', expires=0)
    resp.set_cookie('o4o_token', '', expires=0)
    session.clear()
    return resp
