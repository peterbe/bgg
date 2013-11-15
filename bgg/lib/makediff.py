import os
import json
import subprocess

from . import config


def get_repo_name():
    # `git rev-parse --show-toplevel`
    d = call('git rev-parse --show-toplevel'.split())
    return os.path.split(d)[-1].strip()


def load(branchname):
    data = json.load(open(os.path.expanduser(config.SAVE_FILE)))
    repo_name = get_repo_name()
    try:
        return data['%s:%s' % (repo_name, branchname)]
    except KeyError:
        # possibly one of the old ones
        return data[branchname]


def call(seq):
    """Use Popen to execute `seq` and return stdout."""
    return subprocess.Popen(seq,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT).communicate()[0]


def run():
    branches = call(['git', 'branch'])
    branchname = [
        x.replace('* ', '').strip()
        for x in branches.splitlines()
        if x.startswith('* ')
    ][0]
    data = load(branchname)

    def make_filename(bugnumber, increment=None):
        home = os.path.expanduser('~/tmp/')
        if increment:
            f = os.path.join(home, 'bug%s-%s.diff' % (bugnumber, increment))
        else:
            f = os.path.join(home, 'bug%s.diff' % bugnumber)
            increment = 1
        if os.path.isfile(f):
            return make_filename(bugnumber, increment + 1)
        return f

    filename = make_filename(data['bugnumber'])

    if branchname.startswith('feature/'):
        with open(filename, 'w') as f:
            f.write(call(['git', 'diff', 'develop...']))

    else:
        with open(filename, 'w') as f:
            f.write(call(['git', 'diff', 'master...']))

    print filename
