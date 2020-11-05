from okta_multidemo.util.help import load_help
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()


def main():
    root = 'okta_multidemo/help'
    path = Path(root).absolute()
    static_url = os.getenv('AWS_CLOUDFRONT_URL')
    ct = load_help(path, static_url)
    print('{} help templates created'.format(ct))


if __name__ == '__main__':
    main()
