## View data protected by [API Access Management](https://developer.okta.com/docs/concepts/api-access-management/) (MVC version)

When a user is authenticated, they're issued an access token (in JWT format) which can be used to authorize access to one or more API endpoints.  In this example, the user uses a token which gives read access to an endpoint that returns a list of products.

In the MVC version of this view, the token is stored on the server side, and a server-side component makes the API call. This can be an appropriate architecture for high-security use cases because the token is not stored on the client.

In this demo app, the token is stored in memory in a session object provided by the Flask framework.  In a production deployment, it would likely be persisted in a database instead.

`TODO: diagram`
