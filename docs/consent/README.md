## Setup for API AM scope consent demo

This Kotter feature enables you to demo how an external PKCE client might be authorized to access your app's API.

Before proceeding, first make sure that you've added some items to your "Portfolio" page in your Kotter app by interacting with the Products page.  Go to Tools > Portfolio/Consent to confirm this is the case.

1. Go to Glitch.com and create a New Project, choosing "Import from Github". Use this repo URL: https://github.com/mdorn/pkce-apiam-example
2. "Show" the project "in a new window" to get the URL.
3. In Kotter, go to Tools > Developer and add an OAuth 2.0 client with the Authorization Code (PKCE) grant type.  Enter the URL of your Glitch project from Step 2 as the Redirect URI. (No trailing slash.)  You'll need the resulting Client ID for your Glitch project.
4. In Kotter go to Tools > Admin > Config, and get the Authn Endpoint and Token Endpoint values of your custom Kotter authorization server.
5. In your Glitch project, configure the `config` variables as follows:

- `client_id`: value from step 3 above
- `redirect_url`: the URL of your Glitch project e.g. `https://mdorn-pkce-apiam-example-1.glitch.me`
- `authorization_endpoint`: value from step 4 above
- `token_endpoint`: value from step 4 above
- `api_url`: change the domain part of this to match your Kotter app URL.

Now when you "Show" the Glitch app in a new window, you should be able to authenticate with Okta, give consent, then see your portfolio list in the Glitch app.

Navigate back to Tools > Portfolio/Consent in your Kotter app and notice that you've given consent to the PKCE client that represents the Glitch app.  You can also revoke consent from this screen.
