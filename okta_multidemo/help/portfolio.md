## Portfolio/Consent

The purpose of this page is to display a list of the products/services that a user has purchased/activated in the demo app. There is, however, also an API endpoint offering authorized access to this list for external OAuth clients.

In the Developer Portal, you can add a PKCE client to offer an external application access to this API.  The client will automatically be added to an Access Policy that grants access to the `orders:read:user` scope for authenticated users who belong to a specified group.

In a typical scenario this client would be incorporated into an external application to share data with that external application.  In the below illustration the Resource server is the application you're using now (specifically its API), while the "Client" is the external application.

![oauth image](/static/img/help/oauth_auth_code_flow_pkce.png "OAuth Authorization Code with PKCE Flow")

This access may include [explicitly giving consent](https://developer.okta.com/docs/guides/request-user-consent/overview/) to a particular scope.  Granted consents are listed on this page as well, and the user also has the option to revoke them -- these features use the [`grants` endpoint of the Applications API](https://developer.okta.com/docs/reference/api/apps/#application-oauth-2-0-scope-consent-grant-operations).

To fully understand this flow and how to demo this functionality, see the documentation in the repo [here](https://github.com/udplabs/okta-kotter/tree/master/docs/consent).
