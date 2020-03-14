## Okta Multidemo

The purpose of this application is to demonstrate the integration of a custom app with [Okta](https://www.okta.com/) for identity management and API access management.  Two key features are 1) contextual help: a "Help" button on each page gives technical information about some key aspect of the integration, and 2) themes: you can choose from an included theme or easily create and use a custom theme.

### Install and run

Once you install the application and configure an environment variables file, you can run it and visit http://localhost:5000 in your browser.

#### Run locally

Assuming you have Python 3 installed (tested with v3.7):

```
git clone https://github.com/mdorn/python-okta-multidemo
cd python-okta-multidemo
python3 -m venv env
. env/bin/activate
pip install -r requirements.txt
cp .env.example .env  # modify your .env file with values for your Okta environment
flask run  # or "FLASK_DEBUG=1 FLASK_ENV=development flask run" for debugging etc.
```

#### Run in a Docker container

Once you've pulled the image, be sure to set up a local environment file with the expected values (see `.env.example` at root of the project).  You can then reference that file when you `docker run`.

```
docker pull mdorn/okta-multidemo
docker run --env-file PATH_TO_YOUR_ENV_FILE --name okta-multidemo -p 5000:5000 mdorn/okta-multidemo
```

### Okta org configuration

The demo app expects a few configuration details in your Okta org (TODO: automate configuration with Terraform):

- Create an "Admin" group.
- An "Web" OpenID Connect application with:
  - both Authorization Code and Implicit grant types enabled
  - Login redirect URI: http://localhost:5000
  - Initiate login URI: http://localhost:5000/login/okta/authorized
  - App Profile custom attributes (group type):
    - `app_permissions` with members:
      - display: `Admin`, value: `admin`
      - display: `Premium`, value: `premium`
    - `app_features`: with members:
      - display: `Regular`, value: `regular`
      - display: `Premium`, value: `premium`
- An Authorization Server for audience `http://localhost:5000`:
  - Custom scopes:
    - `products:read`
    - `products:update`
    - `orders:create`
    - `orders:read`
    - `orders:update`
  - Custom claims:
    - Any custom attributes you might have in your user profile(s) that you want to show in the tokens
    - `feature_access`: `appuser.app_features`
    - `role`: `appuser.app_permissions`
    - `groups`: `groups: matches regex .*`
  - Access policies:
    - In your Default Policy set up two rules:
      - Default:
        - If Grant type is Authz Code or Implicit
        - following scopes are requested: `orders:create`, `products:read`, `openid`, `profile`, `email`.
      - Admin:
        - If Grant type is Authz Code or Implicit
        - Group is `Admin`
        - following scopes are requested: `orders:create`, `products:read`, `openid`, `profile`, `email`, `orders:read`, `orders:update`, `products:update`
    - Client Credentials policy (for non-user-driven access like batch jobs etc.)
      - Rule: "Admin client credentials"
        - If Grant type is Client Credentials
        - Group is `Admin`
        - following scopes are requested: `orders:create`, `orders:read`, `orders:update`, `products:update`
    - (Feel free to experiment with Token Hooks on your own here as well)
- Identity Providers (optional, to show social authn, IdP discovery, etc.):
  - For social auth, Google and Facebook are supported -- set your `OKTA_GOOGLE_IDP` and `OKTA_FACEBOOK_IDP` env vars to the appropriate IDs once you've set them up in Okta.
  - For SAML/IdP discovery, set the `OKTA_SAML_IDP` value to the ID of the provider once you've set it up.  Additionally you'll need to set the `OKTA_IDP_REQUEST_CONTEXT` to a value taken from the embed link of your OIDC client, e.g. `/home/oidc_client/0oaar.../aln17...`

It's up to you to configure additional rules for MFA, which users belong to the "Admin" group, etc. to demonstrate in conjunction with the sign-in widget or Okta-hosted sign-in.

### Themes

A theme is a set of files used to customize your demo instance.  They should at a publicly accessible URI, to which you point your `THEME_URI` env variable.  The following built-in themes are available, and can be set by using the localhost URI e.g. `http://localhost:5000/static/themes/books`:

- `books`
- `bank`
- `cloud`
- `default`

To create your own theme, see the `okta_multidemo/static/themes/books` folder for an example.

Themes are structured as follows:

```
my_theme
\- bg.jpg
\- icon-square.png
\- logo.png
\- config.json
\- data.json
\- img-items (optional)
  \- product-image-1.png
  \- product-image-2.png
```

- `bg.jpg`:  A background image for the home page; use either a customer-specific image or a royalty-free image e.g. from [pexels.com](https://www.pexels.com/).
 - `icon-square.png`: A small square icon that will be displayed in the upper left corner of the nav bar, and possibly elsewhere.
- `logo.png`: A small horizontal logo, similar to what you'd see in the upper left of an Okta end user dashboard.
- `config.json`: Configuration details of your theme, including the name/label of the "product" or "service" that is being offered.  If the configuration has `img-items` set to `true`, then the app will expect some custom images in the `img-items` directory of your theme corresopnding to the products/services in `data.json`.  Otherwise `data.json` can reference the stock images found in `okta_multidemo/static/img/items`.  Here's an example from the `books` theme:
```
{
  "label": "books",
  "site-title": "Okta Cloud Books Warehouse",
  "items-title": "Books",
  "items-title-label": "books",
  "action-title": "Restock",
  "img-items": true
}
```
- `data.json`: Defines the products/services that will be listed on the site.  Here's a partial example from the `books` theme:
```
[
    {
        "itemId": "1",
        "title": "Cloud Atlas",
        "description": "",
        "category": "fiction",
        "count": 10,
        "price": 0,
        "image": "cloud_atlas.jpg",
        "target": "PUBLIC"
    },
    {
        "itemId": "2",
        "title": "The Cloud of Unknowing",
        "description": "",
        "category": "nonfiction",
        "count": 10,
        "price": 0,
        "image": "cloud_of_unknowing.jpg",
        "target": "PREMIUM"
    },
    ...
```

A good way to host your theme is simply to drop the files into a publicly accessible AWS S3 bucket, and use the AWS CLI:

    aws s3 sync ./path/to/theme_folder s3://S3_BUCKET_NAME/theme_folder --acl public-read

Then you can set your `THEME_URI` to `https://S3_BUCKET_NAME.s3-us-west-2.amazonaws.com/theme_folder`.

> **NOTE:** if you're running the app locally, you can also simply put your theme in e.g. `okta_multidemo/static/themes/_MY_THEME` and set your `THEME_URI` to `http://localhost:5000/static/themes/_MY_THEME`.

### Acknowledgments

- Bank image by Adrien Coquet from the Noun Project
