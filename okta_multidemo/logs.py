import json
import logging
import os

import coloredlogs
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import Terminal256Formatter
# from pygments.styles import get_style_by_name, get_all_styles
from dotenv import load_dotenv
load_dotenv()


SILENCE_LOGS = [
    'urllib3.connectionpool',
    'simple_rest_client.request',
    'faker.factory',
    'hpack.hpack',
]


def configure_logging():
    log_level = 'DEBUG' if os.environ.get('STAGE') == 'dev' else 'INFO'
    for module in SILENCE_LOGS:
        logging.getLogger(module).setLevel(logging.WARNING)
    logging.basicConfig(level=log_level)
    coloredlogs.install(level=log_level)


def format_json_output(input):
    output = highlight(
        json.dumps(input, indent=2),
        JsonLexer(),
        Terminal256Formatter(style='native')
    )
    return output
