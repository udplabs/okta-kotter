## Authorization Code Flow

Clicking "Log In" on this page will log your user in using an [Okta-hosted](https://developer.okta.com/docs/concepts/okta-hosted-flows/) [Authorization Code Flow](https://developer.okta.com/docs/concepts/auth-overview/#authorization-code-flow).**

![oauth image](/static/img/help/oauth_auth_code_flow.png "OAuth Authorization Code Flow")

[This guide](https://developer.okta.com/docs/guides/custom-hosted-signin/overview/) provides information on how to customize the Okta-hosted sign in page.

Because this application is a [Flask](https://palletsprojects.com/p/flask/) app written in [Python](https://www.python.org/), it makes use of the [Flask-Dance](https://flask-dance.readthedocs.io/en/latest/) library for its OpenID Connect implementation.  See [this repo](https://github.com/mdorn/flask-dance-okta-example) for a simple example implementation with Okta.

No matter which language or platform you're developing on, you will likely use an open source library that implements the [OpenID Connect](https://openid.net/connect/) and [OAuth 2.0](https://oauth.net/2/) protocols.

See the [OAuth 2.0 Overview](https://developer.okta.com/docs/concepts/auth-overview) to understand differences between OAuth flows.

** Note as of this writing, many websites for both enterprise and consumer use cases implement a login approach where identities are authenticated on a separate domain and redirected to the application after authentication. Some examples of consumer-oriented sites that use this approach include:

- Google (Gmail, etc.): for all services users are redirected to `accounts.google.com` for authentication.
- Ikea: users are redirected to `us.accounts.ikea.com` for login.
- Zappos: users are redirected to `auth.zappos.com` for login.
