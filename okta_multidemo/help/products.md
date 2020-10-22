## View data protected by [API Access Management](https://developer.okta.com/docs/concepts/api-access-management/)

When a user is authenticated, an access token (in JWT format) is issued, which can be used to authorize access to one or more API endpoints.  In this example, the user uses a token which gives read access to an endpoint that returns a list of products.

### REST

This application makes use of a REST API called by the client using vanilla Javascript.  The token is stored on the client, either in local or session storage or a cookie, an HTTP POST called via client-side Javascript code uses this value as the `Bearer` token in the Authorization header.

In this demo app, the token is stored in a cookie.

To understand what's happening on this page, open Chrome Developer Tools to the "Network" tab and refresh the page (it may help to filter requests by "XHR"). Notice a call to a `/products` URI.  If you click this, you'll see that a request is being made to the application's "products" API endpoint: `http://localhost:5000/api/products`, including an `Authorization: Bearer` header containing the access token issued by Okta.  Because the API server has validated the token, the response is a list of products.  Click on the action button for one of the items listed here, and you'll see a similar request, this time to the `http://localhost:5000/api/orders` endpoint.

![image](/static/img/help/api_headers.png "API headers")

![image](/static/img/help/api_response.png "API response")

`TODO: diagram`

### MVC

An MVC version of this view might store the token on the server side (likely in a database), with a server-side component making the API call. This can be an appropriate architecture for high-security use cases because the token is not stored on the client.

See also:

- [API Access Management](https://help.okta.com/en/prod/Content/Topics/Security/API_Access.htm)
