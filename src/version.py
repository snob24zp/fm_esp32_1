#!/usr/bin/env python3


STATIC_VERSION = "R231027;master;cd00fe9adece8e493abdef199c610105d022cfcb"

def get_version():    
    import datetime
    import git
    global STATIC_VERSION

    try:
        repo = git.Repo('.', search_parent_directories=True)
        now = repo.head.commit.authored_datetime
        STATIC_VERSION = f"R{(now.year-2000):02d}{now.month:02d}{now.day:02d};{repo.active_branch};{repo.head.commit.hexsha}"
        content = []
        with open(__file__, 'rt') as fd:
            content = fd.readlines()

        for idx in range(len(content)):
            if content[idx].startswith('STATIC_VERSION'):
                content[idx] = f'STATIC_VERSION = "{STATIC_VERSION}"\n'
                break

        with open(__file__, 'wt') as fd:
            fd.writelines(content)

    except git.InvalidGitRepositoryError as ex:
        pass
    return STATIC_VERSION


if __name__ == '__main__':
    print(f'Version: {get_version()}')
