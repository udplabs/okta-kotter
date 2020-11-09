* User not logged in: see **Authorization Code Flow**
* User logged in: see **JSON Web Tokens (JWTs)**

## Authorization Code Flow

Clicking "Log In" on this page will log your user in using an [Okta-hosted](https://developer.okta.com/docs/concepts/okta-hosted-flows/) [Authorization Code Flow](https://developer.okta.com/docs/concepts/auth-overview/#authorization-code-flow).**  The "Resource Server" in the diagram below is not involved until the client issues a request to the application's API, separately from authentication.

![oauth image]({{ STATIC_URL }}/img/help/oauth_auth_code_flow.png "OAuth Authorization Code Flow")

[This guide](https://developer.okta.com/docs/guides/custom-hosted-signin/overview/) provides information on how to customize the Okta-hosted sign in page. Okta-hosted sign in is an alternative to embedding the Okta Sign In Widget in your app.

Because this application is a [Flask](https://palletsprojects.com/p/flask/) app written in [Python](https://www.python.org/), it makes use of the [OAuthLib](https://oauthlib.readthedocs.io/en/latest/) library for its OpenID Connect implementation.

No matter which language or platform you're developing on, you will likely use an open source library that implements the [OpenID Connect](https://openid.net/connect/) and [OAuth 2.0](https://oauth.net/2/) protocols.

See the [OAuth 2.0 Overview](https://developer.okta.com/docs/concepts/auth-overview) to understand differences between OAuth flows.

** Note as of this writing, many websites for both enterprise and consumer use cases implement a login approach where identities are authenticated on a separate domain and redirected to the application after authentication. Some examples of consumer-oriented sites that use this approach include:

- Google (Gmail, etc.): for all services users are redirected to `accounts.google.com` for authentication.
- Ikea: users are redirected to `us.accounts.ikea.com` for login.
- Zappos: users are redirected to `auth.zappos.com` for login.

## JSON Web Tokens (JWTs)

When a user successfully authenticates with Okta via OpenID Connect (OIDC), an access token and an ID token are issued, which can be viewed by clicking the "Tokens" button here (you'll see both the Base64-encoded token and the decoded JSON object).  Each token contains a set of [standard claims](https://openid.net/specs/openid-connect-core-1_0.html#StandardClaims) but can also contain custom claims, which in Okta can map onto a user profile attribute, represent the user's group memberships, etc.

One important standard claim is the `scp` or "scopes" claim in the access token.  When a user authenticates, a set of scopes is requested as part of the OIDC transaction.  If that request is successful according to the Access Policy configured on the Authorization Server (i.e. the user belongs to a group permitted to request those scopes), the scopes are populated into the token.  The user will subsequently use that token as the `Bearer` token in the `Authorization` HTTP for any request to an Okta-protected API endpoint.  That endpoint is responsible for validating the token as part of the authorization.

For more see:

- [OAuth 2.0 Overview](https://developer.okta.com/docs/concepts/auth-overview)
- [Validate Access Tokens](https://developer.okta.com/docs/guides/validate-access-tokens/go/overview/)
- [Validate ID Tokens](https://developer.okta.com/docs/guides/validate-id-tokens/overview/)
