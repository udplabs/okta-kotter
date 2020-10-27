## Kotter on the Unified Demo Platform (UDP)

> **NOTE:** The `README.md` file at the root of the repository directory explains how to install and configure Kotter locally. These instructions are for UDP users.

If you're using Kotter on the Unified Demo Platform (UDP), perform the following steps after provisioning is complete to finish the configuration:

- Add an API key in your Okta tenant in Security > API > Tokens and add it to `okta_api_key` in your Kotter app settings in UDP.
- In your Okta tenant, in Applications > Kotter > Okta API Scopes, grant the following scopes:
    + `okta.users.read`
    + `okta.users.manage`
    + `okta.eventHooks.read`
- **Step-up MFA authentication** (in Tools > Admin > Orders): To approve orders in the admin console, configure Okta Verify as an MFA factor for your administrative user.
- **Developer Portal** (in Tools > Developer).  Perform the following steps:
    - For API scope consent, enable the `API_ACCESS_MANAGEMENT_CONSENT` feature flag in your Okta tenant.  For instructions on how to configure and demo it click [here](../consent).
    - Retrieve the relevant resource ID's from Tools > Admin > Config and copy them into your Kotter UDP config as follows:
        - `ff_developer_cc_policy_id`: "Developer Client Credentials" Authn Server Policy ID
        - `ff_developer_pkce_policy_id`: "Developer PKCE Clients" Authn Server Policy ID
        - `ff_portfolio_client_group`: "Everyone" group ID
- **Event Hooks** (in Tools > Event Hooks): In your Okta tenant, go to Workflow > Event Hooks to create an Event Hook, give it a name and the URL for your Kotter deployment, ending with `api/events`, e.g.: `https://tmd3.kotter.stg.unidemo.info/api/events`.  You'll need to specify one or more events to track, but those events will start showing up on this page of your Kotter app.  Once you've created the hook, go to Tools > Admin > Config in your Kotter app and get the Event Hook ID and set the Kotter UDP config `ff_event_hook_id` to the value you find there.
- **Optional**: To see all the products provided by the API including "Premium" products in some of the themes, a custom claim is used that maps onto the application profile field `app_features`.  To assign this to your user, go to Applications > Kotter > Assignments > \[edit\] to Edit User Assignment, and select "Premium" under "Features".  When you authenticate as this user, the access token will be populated accordingly.  **NOTE:** this is more useful as a Group assignment so that you can for example easily assign a "Premium" group of users access to these features. You'll need the `APPLICATION_ENTITLEMENT_POLICY` and `UD_DEFINE_ENUM_PROPERTIES` feature flags enabled in your tenant for that.

Note that for any changes to the settings in your Kotter app UDP config, you'll need to logout and log back in.  If you change themes, you may want to go to Tools > Admin > Config in your Kotter app and click the "Reset" button to install the theme's product data.

## TODO

- Additional documentation for individual Kotter features.
