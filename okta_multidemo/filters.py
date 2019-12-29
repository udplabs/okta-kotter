import mistune

from dateutil.parser import parse

from .app import app

@app.template_filter('parse_date')
def parse_date(s):
    date_time_obj = parse(s)
    date_fmt = date_time_obj.strftime('%b %d %Y %H:%M:%S')
    return date_fmt


@app.template_filter('parse_markdown')
def parse_markdown(s):
    markdown = mistune.markdown(s)
    return markdown


@app.template_filter('feed_icon')
def feed_icon(link):
    val = 'link'
    for item in app.config['FEEDS']:
        if link.startswith(item['item_url_prefix']):
            val = item['type']
            break
    return val


app.jinja_env.filters['parse_date'] = parse_date
app.jinja_env.filters['parse_markdown'] = parse_markdown
app.jinja_env.filters['feed_icon'] = feed_icon
