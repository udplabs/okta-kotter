## Orders admin

Orders can be fulfilled by an admin user using this interface and the same access token used for other API access in this application (sent as the `Bearer` token in the `Authorization` header), or by an automated process using a machine-to-machine flow faciliated by a [Client Credentials](https://developer.okta.com/docs/guides/implement-client-creds/overview/) client.

**Admin user-driven approval:** When the admin user clicks the "approve" button, and API call is made to the REST API to update an order, using a scope that is only available to administrative users.  This call also involves step-up multifactor authentication, which has been configured using the [Factors API](https://developer.okta.com/docs/reference/api/factors/).

`TODO:` Currently the app uses the first factor configured for the user, and has only been tested with Okta Verify.

**Approval via automated/scheduled task:**  In a machine-to-machine scenario, an automated task that is authenticated via [Client Credentials](https://developer.okta.com/docs/guides/implement-client-creds/overview/) flow makes the appropriate API call.

See `okta_multidemo/scripts/fulfill_orders.py` in the project repo for an example of a script that will perform this function.
