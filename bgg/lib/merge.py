import os
import json
import subprocess

from . import config


def get_repo_name():
    # `git rev-parse --show-toplevel`
    d = call('git rev-parse --show-toplevel'.split())
    return os.path.split(d)[-1].strip()


def save(branchname):
    data = json.load(open(os.path.expanduser(config.SAVE_FILE)))
    repo_name = get_repo_name()
    try:
        del data['%s:%s' % (repo_name, branchname)]
    except KeyError:
        # legacy
        del data[branchname]
    json.dump(data, open(os.path.expanduser(config.SAVE_FILE), 'w'), indent=2)


def call(seq):
    """Use Popen to execute `seq` and return stdout."""
    return subprocess.Popen(seq,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT).communicate()[0]

def load(branchname):
    data = json.load(open(os.path.expanduser(config.SAVE_FILE)))
    repo_name = get_repo_name()
    try:
        return data['%s:%s' % (repo_name, branchname)]
    except KeyError:
        # possibly one of the old ones
        return data[branchname]


def run():
    branches = call(['git', 'branch'])
    branchname = [x.replace('* ', '').strip() for x in branches.splitlines() if x.startswith('* ')][0]
    data = load(branchname)
    _status = call(['git', 'status', '--porcelain'])
    changed = [x for x in _status.splitlines() if not x.startswith('?? ')]
    if changed:
        print "ERROR. Some still changed files"
        print "\t", "\n\t".join(changed)
        exit()

    if data.get('gitflow'):
        print call(['git', 'flow', 'feature', 'finish', branchname.replace('feature/', '')])
    else:
        print call("git checkout master".split())
        print call(['git', 'merge', branchname])
        print call(['git', 'branch', '-d', branchname])

    print "NOW, feel you might want to run:\n"
    if data.get('gitflow'):
        print "git push origin develop"
    else:
        print "git push origin master"
    print

    save(branchname)

    push_for_you = raw_input("Run that push? [Y/n] ").lower().strip()
    if push_for_you not in ('n', 'no'):
        cmd = ['git', 'push', 'origin']
        if data.get('gitflow'):
            cmd.append('develop')
        else:
            cmd.append('master')
        print call(cmd)
