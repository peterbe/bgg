import os
import subprocess


def call(seq):
    """Use Popen to execute `seq` and return stdout."""
    return subprocess.Popen(
        seq,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    ).communicate()[0]


def get_current_branchname():
    branches = get_branches()
    return [
        x.replace('* ', '').strip()
        for x in branches.splitlines()
        if x.startswith('* ')
    ][0]


def get_branches():
    return call(['git', 'branch'])


def get_repo_name():
    # `git rev-parse --show-toplevel`
    d = call('git rev-parse --show-toplevel'.split())[0]
    return os.path.split(d)[-1].strip()
