## View data protected by [API Access Management](https://developer.okta.com/docs/concepts/api-access-management/) (REST/SPA version)

When a user is authenticated, they're issued an access token (in JWT format) which can be used to authorize access to one or more API endpoints.  In this example, the user uses a token which gives read access to an endpoint that returns a list of products.

In the REST version of this view, the token is stored on the client, either in local or session storage or a cookie, an HTTP POST called via client-side Javascript code uses this value as the `Bearer` token in the Authorization header.

In this demo app, the token is stored in a cookie.

To understand what's happening on this page, open Chrome Developer Tools to the "Network" tab and refresh the page (it may help to filter requests by "XHR"). Notice a call to a `/products` URI.  If you click this, you'll see that a request is being made to the application's "products" API endpoint: `http://localhost:5000/api/products`, including an `Authorization: Bearer` header containing the access token issued by Okta.  Because the API server has validated the token, the response is a list of products.  Click on the action button for one of the items listed here, and you'll see a similar request, this time to the `http://localhost:5000/api/orders` endpoint.

![image](/static/img/help/api_headers.png "API headers")

![image](/static/img/help/api_response.png "API response")

`TODO: diagram`

See also:

- [API Access Management](https://help.okta.com/en/prod/Content/Topics/Security/API_Access.htm)
