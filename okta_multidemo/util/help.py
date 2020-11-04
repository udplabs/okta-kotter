import os
import glob
from pathlib import Path

import mistune
from jinja2 import Template

from dotenv import load_dotenv
load_dotenv()


def load_help(help_path, static_url):
    parent_path = Path(help_path).parent.absolute()
    src_path = os.path.join(parent_path, 'help')
    dest_path = os.path.join(parent_path, 'templates', 'help')
    print(src_path, dest_path)
    ct = 0
    for name in glob.glob('{}/**'.format(src_path), recursive=True):
        path = Path(name).parent.absolute()
        file_name = Path(name).name
        file_path = os.path.join(path, file_name)
        if os.path.isfile(file_path):
            with open(file_path) as file_:
                data = file_.read()
                t = Template(data)
                data = t.render(STATIC_URL=static_url)
                help_html = mistune.markdown(data)
            path_fragment = name.replace(src_path, '').replace('.md', '.html')
            dest_file = os.path.join(
                dest_path,
                path_fragment[1:]
            )
            dest_dir = Path(dest_file).parent.absolute()
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            with open(dest_file, 'w') as html_:
                html_.write(help_html)
            ct += 1
    return ct
