## Admin section

To access this section, a separate OIDC call to the Authorization Server is made, requesting the scopes associated with administrative API access (e.g. `orders:update`).  If the user is able to access these scopes in accordance with the [Access Policy](https://help.okta.com/en/prod/Content/Topics/Security/API_Access.htm) configured on the [Authorization Server](https://developer.okta.com/docs/concepts/auth-servers/) in Okta, then the request will succeed and the user will be redirected to the Admin section of the site, and the application will be able to make successful REST API calls for the user.

This separate OIDC call is transparent to the end user, because the flow will check for an existing session and not prompt the user if it exists.
