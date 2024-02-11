import os
import pathlib
import markdown
from wikilinks import WikiLinkExtension


def gen_html(path, output_path):
    for f in pathlib.Path(path).iterdir():
        if f.is_file():
            if f.suffix == '.md':
                html = markdown.markdown(f.read_text('utf-8'), extensions=['tables', 'nl2br',
                                         'fenced_code', WikiLinkExtension(base_url="", end_url='.md.html')])
                _fname = pathlib.Path(output_path + '/' + f.name.replace(' ', '_') + '.html')
                print(f"{f.absolute()} => {_fname.absolute()}")
                _fname.write_text(html)
        elif f.is_dir():
            os.makedirs(output_path + '/' + f.name.replace(' ', '_'), exist_ok=True)
            gen_html(f.absolute(), output_path + '/' + f.name.replace(' ', '_'))


if __name__ == "__main__":
    os.makedirs('./out/docs', exist_ok=True)
    gen_html('./doc', './out/docs')
