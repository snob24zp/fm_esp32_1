import os
import pathlib
import markdown
from wikilinks import WikiLinkExtension
from jinja2 import Template


def tpl_hnd(html:str, output_file:pathlib.Path):
    tmpl = Template(pathlib.Path('./ci/doc.template.jinja2').read_text())
    output_file.write_text(tmpl.render(body=html))

def gen_html(path, output_path):
    for f in pathlib.Path(path).iterdir():
        if f.is_file():
            if f.suffix == '.md':
                html = markdown.markdown(f.read_text('utf-8'), extensions=['tables', 'nl2br',
                                         'fenced_code', WikiLinkExtension(base_url="", end_url='.md.html')])
                _fname = pathlib.Path(output_path + '/' + f.name.replace(' ', '_') + '.html')
                print(f"{f.absolute()} => {_fname.absolute()}")
                tpl_hnd(html, _fname)
        elif f.is_dir():
            os.makedirs(output_path + '/' + f.name.replace(' ', '_'), exist_ok=True)
            gen_html(f.absolute(), output_path + '/' + f.name.replace(' ', '_'))


if __name__ == "__main__":
    os.makedirs('./out/docs', exist_ok=True)
    gen_html('./doc', './out/docs')
