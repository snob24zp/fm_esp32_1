#!/usr/bin/python3
import sys
import datetime
import git
from jinja2 import Template

with open('./ci/release-page/index.html') as f:
    tmpl = Template(f.read())
    repo = git.Repo('.')
    commits = []
    for c in list(repo.iter_commits(sys.argv[2], max_count=5)):
        commit_lnk = f'<a href="https://github.com/-/{c.hexsha}">{c.hexsha}</a>'
        msg_wlnk = ""
        for word in c.message.split(' '):
            if word[0] == '#':
                word = f'<a href="https://tasks.dlab.pw/issues/{word[1:]}">{word}</a>'
            msg_wlnk += word
            msg_wlnk += ' '

        commits.append([msg_wlnk, commit_lnk, datetime.datetime.fromtimestamp(c.committed_date)])

    print(tmpl.render( release=sys.argv[1], commit=commits[0][1], tm=datetime.datetime.now(), commits=commits))

