## Client Credentials flow in action

This testing tool demonstrates using the client credentials flow to:

1. Get an appropriately scoped access token from the authorization server using the client's ID and secret.
2. Use that token to access an application's API endpoint.

In this application, the API endpoint inspects the token to ensure it is valid and properly scoped before returning any data.

![CC](/static/img/help/oauth_client_creds_flow.png "Client Credentials flow")
