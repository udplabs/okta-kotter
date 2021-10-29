![logo](docs/img/kotter_okta.png)

## Table of Contents

- [Table of Contents](#table-of-contents)
- [About](#about)
  * [Components](#components)
- [Quickstart](#quickstart)
  * [Get an Okta tenant](#get-an-okta-tenant)
  * [Clone and install this repo.](#clone-and-install-this-repo)
  * [Terraform your Okta tenant](#terraform-your-okta-tenant)
  * [Run the app](#run-the-app)
- [Next steps](#next-steps)
  * [Themes](#themes)
  * [Completing the configuration](#completing-the-configuration)
- [Troubleshooting](#troubleshooting)
- [Acknowledgements](#acknowledgements)

## About

Kotter educates Okta [sweathogs](https://en.wikipedia.org/wiki/Welcome_Back,_Kotter) about what goes on under the hood of a custom app integration with [Okta](https://www.okta.com/) for CIAM and API Access Management use cases. It's also suitable as a themeable demo platform.

![gif](docs/img/okta-multidemo-screencast.gif)

Two key features are 1) contextual help: a "Teach" button on each page gives technical information about some key aspect of the feature on the page, and 2) themes: you can choose from an included theme or easily create and use a custom theme.

### Components

Kotter currently offers the following components:

- **Login with Okta:** the Okta Sign-in Widget is configured in various ways to demonstrate authentication (including support for Social Authentication and inbound federation/external IdP discovery, which need to be configured separately).  A button to launch Okta-hosted login is also available.
- **API Access Management (API AM)** - a RESTful API serves a catalog of product offerings, and some front-end vanilla Javascript interacts with it for both viewing the products and placing an order, authorizing transactions with an Okta-issued access token.
- A simple **admin console** that demonstrates the following features:
  + **OAuth for Okta (O4O)** for accessing a list of users.
  + **Step-up MFA** for approving an order using the Factors API.
- A **developer portal** and a product portfolio page work together to demonstrate:
  - **Client Credentials flow for M2M use cases**.
  - **Consent management** for OAuth scopes, especially when the API is accessed by a client using **PKCE flow** residing on an external domain.
- **Event hooks** (also uses O4O): a screen that reports events happening in the connected Okta instance in near real time.  (Requires the app to be running at a publicly accessible URL, e.g. on UDP. See [here](docs/consent) for config details.
- **App dashboard**: a simple SSO dashboard that displays clickable icons for all the apps assigned to the authenticated user.

## Quickstart

> **NOTE**: Kotter also runs on the Okta Unified Demo Platform (UDP).  The instructions below are for running it locally. Instructions for additional configuration after UDP provisioning are [here](docs/udp).

The following steps are needed to get up and running:

1) [Get an Okta tenant](#get-an-okta-tenant).
2) [Clone and install this repo](#clone-and-install-this-repo).
3) [Terraform your Okta tenant](#terraform-your-okta-tenant).

Details below.

### Get an Okta tenant

- Create a free Okta developer org [here](https://developer.okta.com/). (The [Okta CLI](https://github.com/oktadeveloper/okta-cli) is also a good way to do this.)  Once you've created it, login and [create an API token](https://developer.okta.com/docs/guides/create-an-api-token/overview/).  You'll need that for the Terraform step below.

### Clone and install this repo.

- Assuming you have Python 3 installed (tested with v3.7 and 3.8), clone this repo and install the requirements:

```bash
git clone https://github.com/udplabs/okta-kotter
cd okta-kotter
python3 -m venv env
. env/bin/activate
pip install -r requirements.txt
```

Remain in the working directory for all of the remaining steps.

### Terraform your Okta tenant

These steps will create the necessary resources in your Okta tenant for Kotter to function using [Terraform](https://www.terraform.io/).  (If you're unfamiliar with using Terraform with Okta, see [this blog post](https://developer.okta.com/blog/2020/02/03/managing-multiple-okta-instances-with-terraform-cloud).)

- Copy `okta.auto.tfvars.example` to `okta.auto.tfvars` and populate the `org_name`, `base_url` and `api_token` values in the file.  It will look something like this:

```
org_name  = "dev-123456"
base_url  = "okta.com"
api_token = "00abc123..."
```

- Run Terraform as follows:

```
terraform init
terraform plan
terraform apply
```

- Copy the resulting environment variables file: `cp .env.terraformed .env`

> **NOTE:** Because of a bug in the current Terrafrom script, you'll need to manually create a group called "Admin" and assign your user to it in the Okta admin console to access all available Kotter functionality.

### Run the app

- Run the app: `flask run`
- Navigate your browser to `http://localhost:5000`.  You'll be able to log in and interact with the product catalog, but some functionality won't be available until you take the next steps described below.

## Next steps

### Themes

Try changing the theme by setting the `THEME` .env variable from `default` to one `bank`, `books`, or `cloud`.  Not only does the look and feel change, but the product catalog changes as well, if you delete or reset the database.

You may also use a theme hosted at an external URL by modifying `.env` as shown below:

    THEME=https://textmethod-demo-themes.s3-us-west-2.amazonaws.com/_league

### Completing the configuration

Terraform cannot fully populate your Okta tenant with the necessary configuration for all Kotter functionality.

To complete the setup, take the following steps in your Okta tenant:

- In Applications > Kotter > Okta API Scopes, grant the following scopes:
  + `okta.users.read`
  + `okta.eventHooks.read`
  + `okta.users.manage`

For additional setup info relevant to both a local install and a UDP deployment, see these [Kotter on the Unified Demo Platform (UDP)](docs/udp).

## Troubleshooting

- Currently refresh tokens are not used.  If you run into authorization or other errors, try logging out or clicking the "Reset" button to clear the database and start a new session.

## Acknowledgements

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
