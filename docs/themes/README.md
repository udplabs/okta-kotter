## Themes

The following built-in themes are available:

- `books`
- `bank`
- `cloud`
- `default`

However you can also use a custom theme, the files for which should reside at a publicly accessible URI, to which you point your `THEME` environment variable.

To create your own theme, see the `okta_multidemo/static/themes/books` folder for an example.

Themes are structured as follows:

```
theme_folder
\- bg.jpg
\- icon.png
\- config.json
\- data.json
\- img-items (optional)
  \- product-image-1.png
  \- product-image-2.png
\- logo.png (optional)
```

- `bg.jpg`:  A background image for the home page; use either a customer-specific image or a royalty-free image e.g. from [pexels.com](https://www.pexels.com/).
 - `icon.png`: A small square icon that will be displayed in the upper left corner of the nav bar and the sign-in widget.
- `config.json`: Configuration details of your theme, including the name/label of the "product" or "service" that is being offered.  If the configuration has `img-items` set to `true`, then the app will expect some custom images in the `img-items` directory of your theme corresopnding to the products/services in `data.json`.  Otherwise `data.json` can reference the stock images found in `okta_multidemo/static/img/items`.  Here's an example from the `books` theme:
```json
{
  "label": "books",
  "site-title": "Okta Cloud Books Warehouse",
  "items-title": "Books",
  "items-title-label": "books",
  "action-title": "Restock",
  "img-items": true
}
```
- `data.json`: Defines the products/services that will be listed on the site.  Here's a partial example from the `books` theme:
```json
[
    {
        "itemId": "1",
        "title": "Cloud Atlas",
        "description": "",
        "category": "fiction",
        "count": 10,
        "price": 0,
        "image": "cloud_atlas.jpg",
        "target": "PUBLIC"
    },
    {
        "itemId": "2",
        "title": "The Cloud of Unknowing",
        "description": "",
        "category": "nonfiction",
        "count": 10,
        "price": 0,
        "image": "cloud_of_unknowing.jpg",
        "target": "PREMIUM"
    }
]
```
- `logo.png` (optional, not currently used in app): A small horizontal logo, similar to what you'd see in the upper left of an Okta end user dashboard.

A good way to host your theme is simply to drop the files into a publicly accessible AWS S3 bucket using the AWS CLI:

    aws s3 sync ./path/to/theme_folder s3://S3_BUCKET_NAME/theme_folder --acl public-read

Then you can set your `THEME_URI` to `https://S3_BUCKET_NAME.s3-us-west-2.amazonaws.com/theme_folder`.

> **NOTE:** if you're running the app locally, you can also simply put your theme in e.g. `okta_multidemo/static/themes/_MY_THEME` and set your `THEME_URI` to `http://localhost:5000/static/themes/_MY_THEME`.
