## JSON Web Tokens (JWTs)

When a user successfully authenticates with Okta via OpenID Connect (OIDC), they're issued an access token and an ID token, which can be viewed by clicking the "Tokens" button here (you'll see both the Base64-encoded token and the decoded JSON object).  Each token contains a set of [standard claims](https://openid.net/specs/openid-connect-core-1_0.html#StandardClaims) but can also contain custom claims, which in Okta can map onto a user profile attribute, represent the user's group memberships, etc.

One important standard claim is the `scp` or "scopes" claim in the access token.  When a user authenticates, he or she requests a set of scopes as part of the OIDC transaction.  If that request is successful according to the Access Policy configured on the Authorization Server (i.e. the user belongs to a group permitted to request those scopes), the scopes are populated into the token.  The user will subsequently use that token as the `Bearer` token in the `Authorization` HTTP for any request to an Okta-protected API endpoint.  That endpoint is responsible for validating the token as part of the authorization.

For more see:

- [OAuth 2.0 Overview](https://developer.okta.com/docs/concepts/auth-overview)
- [Validate Access Tokens](https://developer.okta.com/docs/guides/validate-access-tokens/go/overview/)
- [Validate ID Tokens](https://developer.okta.com/docs/guides/validate-id-tokens/overview/)
