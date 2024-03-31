#!/usr/bin/env python3

"""Provides device version, use STATIC_VERSION on device, and get_version() to rebuild this file"""
STATIC_VERSION = "R240331;master;5183e637011d54c26955b17b85024fc74d20124c"

def get_version():
    """Function to rebuild the device version string"""
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

    except git.InvalidGitRepositoryError:
        pass
    return STATIC_VERSION


if __name__ == '__main__':
    print(f'Version: {get_version()}')
