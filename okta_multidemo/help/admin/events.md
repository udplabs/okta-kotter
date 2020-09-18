## Event hooks

This page will display information about events occurring in your Okta tenant when you've configured an [Event Hook](https://developer.okta.com/docs/concepts/event-hooks/) to send a payload about the event to your application's API.  Be sure to configure the `FF_EVENTS_HOOK_ID` environment variable.

E.g. if you have an Event hook configured to listen for "User signed in and session started" (`user.session.start`), when that event happens in your tenant, you'll see it show up here.

The page requires an [OAuth for Okta](https://developer.okta.com/docs/guides/implement-oauth-for-okta/overview/) token for the `okta.eventHooks.read` scope, to list all of the [eligible events](https://developer.okta.com/docs/concepts/event-hooks/?#which-events-are-eligible) that the Event Hook has been configured for, so ensure your administrative user has an appropriate role (Super Administrator does the trick.)
