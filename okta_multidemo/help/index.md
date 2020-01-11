## Authorization Code Flow

Clicking "Log In" on this page will log your user in using an [Okta-hosted](https://developer.okta.com/docs/concepts/okta-hosted-flows/) [Authorization Code Flow](https://developer.okta.com/docs/concepts/auth-overview/#authorization-code-flow).

![example image](/static/img/help/oauth_auth_code_flow.png "An exemplary image")

[This guide](https://developer.okta.com/docs/guides/custom-hosted-signin/overview/) provides information on how to customize the Okta-hosted sign in page.

This application makes use of the [Flask-Dance](https://flask-dance.readthedocs.io/en/latest/) library for its OpenID Connect implementation.  See [this repo](https://github.com/mdorn/flask-dance-okta-example) for a simple example implementation with Okta.

See the [OAuth 2.0 Overview](https://developer.okta.com/docs/concepts/auth-overview) to understand differences between OAuth flows.
