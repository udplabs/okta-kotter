import os
import glob
from pathlib import Path

import mistune


def main():
    root = 'okta_multidemo/help'
    parent_path = Path(root).parent.absolute()
    dest_path = os.path.join(parent_path, 'templates', 'help')
    ct = 0
    for name in glob.glob('okta_multidemo/help/**', recursive=True):
        path = Path(name).parent.absolute()
        file_name = Path(name).name
        file_path = os.path.join(path, file_name)
        # print(file_path)
        # import pdb;pdb.set_trace()
        if os.path.isfile(file_path):
            # print('###', Path(name).parent)
            with open(file_path) as file_:
                data = file_.read()
                help_html = mistune.markdown(data)
            path_fragment = name.replace(root, '').replace('.md', '.html')
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
    print('{} help templates created'.format(ct))


if __name__ == '__main__':
    main()
