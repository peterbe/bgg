import os
import subprocess


def call_and_error(seq, and_print=False):
    """Use Popen to execute `seq` and return stdout."""
    if isinstance(seq, basestring):
        seq = seq.split()
    return subprocess.Popen(
        seq,
        stdout=subprocess.PIPE,
        stderr=and_print and subprocess.STDOUT or subprocess.PIPE
    ).communicate()


def call(seq, and_print=False):
    """Use Popen to execute `seq` and return stdout."""
    return call_and_error(seq, and_print=and_print)[0]


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
    d = call('git rev-parse --show-toplevel'.split())
    return os.path.split(d)[-1].strip()
