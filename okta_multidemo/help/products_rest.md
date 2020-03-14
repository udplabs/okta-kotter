## View data protected by [API Access Management](https://developer.okta.com/docs/concepts/api-access-management/) (REST/SPA version)

When a user is authenticated, they're issued an access token (in JWT format) which can be used to authorize access to one or more API endpoints.  In this example, the user uses a token which gives read access to an endpoint that returns a list of products.

In the REST version of this view, the token is stored on the client, either in local or session storage or a cookie, an HTTP POST called via client-side Javascript code uses this value as the `Bearer` token in the Authorization header.

In this demo app, the token is stored in a cookie.

`TODO: diagram`

See also:

- [API Access Management](https://help.okta.com/en/prod/Content/Topics/Security/API_Access.htm)
