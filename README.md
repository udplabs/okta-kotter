## Table of Contents

- [Okta Multidemo](#okta-multidemo)
  * [Install and run](#install-and-run)
    + [Run locally](#run-locally)
    + [Run in a Docker container](#run-in-a-docker-container)
  * [Okta org configuration](#okta-org-configuration)
    + [Optional configuration](#optional-configuration)
      - [Developer](#developer)
      - [Portfolio](#portfolio)
  * [Themes](#themes)
  * [Troubleshooting and limitations](#troubleshooting-and-limitations)
    + [Mismatching State Error](#mismatching-state-error)
    + [Expiring access tokens](#expiring-access-tokens)
    + [Step-up MFA in Admin](#step-up-mfa-in-admin)
  * [Acknowledgments](#acknowledgments)

## Okta Multidemo

The purpose of this application is to demonstrate the integration of a custom app with [Okta](https://www.okta.com/) for identity management and API access management.  Two key features are 1) contextual help: a "Help" button on each page gives technical information about some key aspect of the integration, and 2) themes: you can choose from an included theme or easily create and use a custom theme.

![gif](okta_multidemo/static/img/okta-multidemo-screencast.gif)

### Install and run

Once you install the application and configure an environment variables file, you can run it and visit http://localhost:5000 in your browser.

> **NOTE:** Minimally populate at least the following block in your `.env` (for more see [Okta org configuration](#okta-org-configuration) below):

    OKTA_BASE_URL=
    OKTA_API_KEY=
    OKTA_CLIENT_ID=
    OKTA_CLIENT_SECRET=
    OKTA_ISSUER=

#### Run locally

Assuming you have Python 3 installed (tested with v3.7):

```bash
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

```bash
docker pull mdorn/okta-multidemo
docker run --env-file PATH_TO_YOUR_ENV_FILE --name okta-multidemo -p 5000:5000 mdorn/okta-multidemo
```

### Okta org configuration

- Install Terraform using the official [Hashicorp installation guide](https://learn.hashicorp.com/terraform/getting-started/install.html)
- Copy the `okta.auto.tfvars.example` file to `okta.auto.tfvars`
- Edit `okta.auto.tfvars` and fill it with real values for your Okta org
- Initalize Terraform with this command: `terraform init`
- Make sure that you correctly set up your `.tfvars` file with this command: `terraform plan`
- If everything looks good, run Terraform using this command: `terraform apply`
- You should now be able to run this demo app using `flask run`

### Manual Okta org configuration

The demo app expects a few configuration details in your Okta org:

- A group called "Admin" -- you'll want to assign at least one user to it.
- API key.
- A "Web" OpenID Connect application with:
  - both Authorization Code and Implicit grant types enabled
  - Login redirect URI:
    - `http://localhost:5000`
    - `http://localhost:5000/authorization-code/callback`
    - `http://localhost:5000/implicit/callback`
  - Initiate login URI: `http://localhost:5000/authorization-code`
  - Okta API Scopes:
    - Grant the `okta.users.read` scope. Users who are both in the "Admin" group and who have an appropriate Okta Administrative role will be able to get a list of users in the app's administrative section using OAuth for Okta.
  - App Profile custom attributes (group type):
    - `app_permissions` with members:
      - display: `Admin`, value: `admin`
      - display: `Premium`, value: `premium`
    - `app_features`: with members:
      - display: `Regular`, value: `regular`
      - display: `Premium`, value: `premium`
- (Optionally) an "OAuth Service" or Client Credentials client.
- Be sure to add `http://localhost:5000` as a Trusted Origin in Security > API.
- An Authorization Server for audience `http://localhost:5000`:
  - Custom scopes:
    - `products:read`
    - `products:update`
    - `orders:create`
    - `orders:read`
    - `orders:update`
  - Custom claims:
    - Any custom attributes you might have in your user profile(s) that you want to show in the tokens
    - Access token (Expressions):
      - `feature_access`: `appuser.app_features`
      - `role`: `appuser.app_permissions`
    - ID token (make this one a `Groups` value type which `Matches regex`):
      - `groups`: `.*`
  - Access policies:
    - In your Default Policy set up two rules:
      - Default:
        - If Grant type is Authz Code or Implicit
        - following scopes are requested: `orders:create`, `products:read`, `openid`, `profile`, `email`.
      - Admin (**IMPORTANT**: drag this rule to the top so that it's the first rule evaluated):
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

#### Optional configuration

Configuration for optional "Tools" enabled by environment feature flags follows.

##### Developer

For Client Credentials clients, in your Authorization Server, create an Access Policy with a Rule that allows `Client Credentials` clients to access the `products:read` scope.  Get the ID of that access policy and assign it in your `.env` file:

```
FF_DEVELOPER=true
FF_DEVELOPER_CC_POLICY_ID=00p...
```

For Authorization Code (PKCE) flow clients, and to demonstrate consent, create a policy with a rule for the `orders:read:user` scope.  Assign that policy ID to `FF_DEVELOPER_PKCE_POLICY_ID`.  Any users who will authenticate using an app that connects with your Okta tenant using this newly created client should belong to a group whose ID has been assigne to `FF_PORTFOLIO_CLIENT_GROUP`.

See [this repo](https://github.com/mdorn/pkce-vanilla-js/blob/consent-demo/index.html) for an example app to use this client.

##### Portfolio

See note about `FF_PORTFOLIO_CLIENT_GROUP` above.

### Themes

A theme is a set of files used to customize your demo instance.  Theme files should reside at a publicly accessible URI, to which you point your `THEME_URI` env variable.  The following built-in themes are available, and can be set by using the localhost URI e.g. `http://localhost:5000/static/themes/books`:

- `books`
- `bank`
- `cloud`
- `default`

To create your own theme, see the `okta_multidemo/static/themes/books` folder for an example.

Themes are structured as follows:

```
theme_folder
\- bg.jpg
\- icon.png
\- config.json
\- data.json
\- img-items (optional)
  \- product-image-1.png
  \- product-image-2.png
\- logo.png (optional)
```

- `bg.jpg`:  A background image for the home page; use either a customer-specific image or a royalty-free image e.g. from [pexels.com](https://www.pexels.com/).
 - `icon.png`: A small square icon that will be displayed in the upper left corner of the nav bar and the sign-in widget.
- `config.json`: Configuration details of your theme, including the name/label of the "product" or "service" that is being offered.  If the configuration has `img-items` set to `true`, then the app will expect some custom images in the `img-items` directory of your theme corresopnding to the products/services in `data.json`.  Otherwise `data.json` can reference the stock images found in `okta_multidemo/static/img/items`.  Here's an example from the `books` theme:
```json
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
```json
[
    {
        "itemId": "1",
        "name": "Cloud Atlas",
        "description": "",
        "category": "fiction",
        "count": 10,
        "price": 0,
        "image": "cloud_atlas.jpg",
        "target": "PUBLIC"
    },
    {
        "itemId": "2",
        "name": "The Cloud of Unknowing",
        "description": "",
        "category": "nonfiction",
        "count": 10,
        "price": 0,
        "image": "cloud_of_unknowing.jpg",
        "target": "PREMIUM"
    }
]
```
- `logo.png` (optional, not currently used in app): A small horizontal logo, similar to what you'd see in the upper left of an Okta end user dashboard.

A good way to host your theme is simply to drop the files into a publicly accessible AWS S3 bucket using the AWS CLI:

    aws s3 sync ./path/to/theme_folder s3://S3_BUCKET_NAME/theme_folder --acl public-read

Then you can set your `THEME_URI` to `https://S3_BUCKET_NAME.s3-us-west-2.amazonaws.com/theme_folder`.

> **NOTE:** if you're running the app locally, you can also simply put your theme in e.g. `okta_multidemo/static/themes/_MY_THEME` and set your `THEME_URI` to `http://localhost:5000/static/themes/_MY_THEME`.

### Troubleshooting and limitations

#### Mismatching State Error

You may occasionally see a `oauthlib.oauth2.rfc6749.errors.MismatchingStateError` with the following warning::

    oauthlib.oauth2.rfc6749.errors.MismatchingStateError: (mismatching_state) CSRF Warning! State not equal in request and response.

This may happen as a result of various demo login configurations using different state variables.  If this happens, ensure you're using a browser session with no cookies set for your local app's domain -- either clear the cookies manually or restart a new browser session (e.g. using incognito or private browsing mode).

#### Expiring access tokens

As of this writing, refresh tokens have not been implemented, so calls to the API backend may fail (possibly silently) after the token has expired.  You may need to logout and hit the API with a fresh session.

#### Step-up MFA in Admin

In order for the step-up MFA challenge to trigger (when you click the "approve" button on an order in the Admin tool), the admin user used for demoing needs to have *only* the Okta Verify factor enrolled.  Ensure this is the case by checking the API `{{url}}/api/v1/users/{{userId}}/factors`.

### Acknowledgments

[Noun Project](https://thenounproject.com/) images:

- Bank by Adrien Coquet from the Noun Project: `okta_multidemo/static/themes/bank/icon.png` and `logo.png`
- Cloud by Kmg Design from the Noun Project: `okta_multidemo/static/themes/cloud/icon.png` and `logo.png`
- Anvil by Michael Wohlwend from the Noun Project: `okta_multidemo/static/img/items/anvil.png`
- storage by Gregor Cresnar from the Noun Project: `okta_multidemo/static/img/items/storage.png`
- Server by Begin sapdian from the Noun Project: `okta_multidemo/static/img/items/server.png`
- Load Balancer by Mani Cheng from the Noun Project: `okta_multidemo/static/img/items/load-balancer.png`
- Card by Daily Icons from the Noun Project: `okta_multidemo/static/img/items/card.png`
- Report by Alfredo at IconsAlfredo.com from the Noun Project: `okta_multidemo/static/img/items/report.png`
- Plunger TNT by Creaticca Creative Agency from the Noun Project: `okta_multidemo/static/img/items/tnt.png`
