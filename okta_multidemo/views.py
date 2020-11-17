import json

from flask import (
    current_app,
    make_response,
    redirect,
    render_template,
    request,
    Response,
    session,
    url_for,
)

from .app import app
from .forms import LoginForm, ProfileForm
from .util import (
    APIClient, decode_token, OktaAPIClient, init_db,
    init_settings, set_session_vars
)
from .util.widget import get_widget_config
from .util.settings import app_settings
from .util.decorators import login_required
from .models import get_model, TENANT_MODELS


@app.route('/', methods=['GET', 'POST'])
def index():
    access_token = request.cookies.get('access_token')
    id_token = request.cookies.get('id_token')
    token_dict = {}
    if access_token:
        access_decoded = decode_token(access_token)
        id_decoded = decode_token(id_token)
        access_payload_fmt = json.dumps(access_decoded, indent=4)
        id_payload_fmt = json.dumps(id_decoded, indent=4)
        token_dict = {
            'id': {
                'token': id_token,
                'payload': id_payload_fmt,
            },
            'access': {
                'token': access_token,
                'payload': access_payload_fmt,
            },
        }
    resp = make_response(render_template(
        'index.html',
        data=token_dict,
        body_class='home-body-image',
        config=app_settings()
    ))
    return resp


@app.route('/status', methods=['GET'])
def status():
    return 'OK'


def render_login_template(conf, settings, css=None):
    resp = render_template(
        'login/widget.html',
        widget_conf=json.dumps(conf, indent=2),
        body_class='home-body-image' if not css else 'home-body-bgcolor',
        custom_css=css,
        config=settings
    )
    return resp


@app.route('/login-widget', methods=['GET'])
def login_widget():
    settings = app_settings()
    conf = get_widget_config(settings)
    return render_login_template(conf, settings)


@app.route('/login-social', methods=['GET'])
def login_widget_social():
    settings = app_settings()
    conf = get_widget_config(settings, 'social')
    return render_login_template(conf, settings)


@app.route('/login-implicit', methods=['GET'])
def login_widget_implicit():
    settings = app_settings()
    conf = get_widget_config(settings, 'implicit')
    return render_login_template(conf, settings)


@app.route('/login-custom-css', methods=['GET'])
def login_widget_custom_css():
    settings = app_settings()
    conf = get_widget_config(settings)
    return render_login_template(conf, settings, css='okta-signin-custom')


@app.route('/login-idp-disco', methods=['GET'])
def login_idp_disco():
    settings = app_settings()
    conf = get_widget_config(settings, 'idp-disco')
    return render_login_template(conf, settings)


@app.route('/login-custom', methods=['GET'])
def login_custom():
    resp = render_template(
        'login/custom.html', form=LoginForm(), config=app_settings())
    return resp


@app.route('/implicit/callback', methods=['POST'])
def implicit_callback():
    # if request.form:
    #     access_token = request.form['access_token']
    #     id_token = request.form['id_token']
    # else:
    data = json.loads(request.data)
    access_token = data['tokens']['accessToken']['value']
    id_token = data['tokens']['idToken']['value']
    set_session_vars(session, id_token)
    resp = make_response(Response(json.dumps({'status': 'OK'}), 200)) # redirect(url_for('index'))
    resp.set_cookie('access_token', access_token)
    resp.set_cookie('id_token', id_token)
    return resp


@app.route('/subscribe', methods=['GET'])
def subscribe():
    resp = render_template('subscribe.html', config=app_settings())
    return resp


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(display_name=session.get('full_name', ''))
    if request.method == 'POST':
        if form.validate():
            params = {
                # ...
                'csrf': session['csrf'],
            }
            pass
    resp = render_template(
        'profile.html',
        form=form,
        config=app_settings()
    )
    return resp


@app.route('/products', methods=('GET',))
@login_required
def products():
    settings = app_settings()
    return render_template('products-rest.html', config=settings)


def products_mvc(settings):
    # NOTE: UNUSED
    # NOTE: Here the view calls the REST API, rather than importing the model directly.
    #   In an MVC app it doesn't have to work this way.
    client = APIClient(app.config['API_URL'], request.cookies.get('access_token'))
    client.api.add_resource(resource_name='products')
    data = client.api.products.list()
    if app_settings()['ITEMS_IMG']:
        img_path = '{}/img-items/'.format(app_settings()['THEME_URI'])
    else:
        img_path = '{}/static/img/items/'.format(app_settings()['APP_URL'])
    return render_template(
        'products.html',
        items=data.body,
        img_path=img_path,
        config=settings
    )


@app.route('/apps', methods=('GET',))
@login_required
def apps():
    settings = app_settings()
    okta = OktaAPIClient(
        settings['OKTA_BASE_URL'],
        settings['OKTA_API_KEY']
    )
    okta.api.add_resource(resource_name='apps')
    data = okta.api.apps.list(params={
        'filter': 'user.id eq "{}"'.format(session['user_id']),
        'limit': 100
    })
    return render_template(
        'apps.html',
        apps=data.body,
        config=settings
    )


@app.route('/_reset', methods=('GET',))
@login_required
def reset():
    # TODO: protect
    env = current_app.config['ENV']
    for model in TENANT_MODELS:
        model = get_model(model)
        model.purge()
    subdomain = session.get('subdomain')
    tenants = get_model('tenants')
    tenants.delete('name', subdomain)
    init_settings(env)
    init_db(env, subdomain)
    if request.args.get('logout'):
        return redirect(url_for('auth.logout'))
    else:
        return redirect('/')
