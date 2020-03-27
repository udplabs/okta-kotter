## Developer Portal

In this section the user can create OAuth 2.0 clients so that external applications can access the resources being protected by Okta's API Access Management.

There are two basic use cases that correspond to two different OAuth 2.0 grant types:

- [Client Credentials](https://developer.okta.com/docs/concepts/auth-overview/#client-credentials-flow) flow: for machine-to-machine (M2M) communication scenarios. A developer can use the client ID and secret, along with a permitted scope, to query an application's API endpoint.  For example, developer has their own website (App A) that they want to populate with this applicaton's (App B) product data.  They might have a nightly batch job that gathers that data, using this Client Credentials client to securely access it.
- [Authorization Code](https://developer.okta.com/docs/concepts/auth-overview/#authorization-code-flow) flow (not yet supported): A developer can use the client ID and secret to establish an OIDC connection with from their own app (App A) to the authorization server of this app (App B) responsible for protecting the app's API (or "Resource Server").  Then users from their app can authorize App A to get their data in App B, which may include [explicitly giving consent](https://developer.okta.com/docs/guides/request-user-consent/overview/) to a particular scope.

**`TODO:`** Authorization Code grant type is not yet supported.
