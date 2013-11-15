import os
import json

from . import config
from . import utils


def save(branchname):
    data = json.load(open(os.path.expanduser(config.SAVE_FILE)))
    repo_name = utils.get_repo_name()
    try:
        del data['%s:%s' % (repo_name, branchname)]
    except KeyError:
        # legacy
        del data[branchname]
    json.dump(data, open(os.path.expanduser(config.SAVE_FILE), 'w'), indent=2)


def load(branchname):
    data = json.load(open(os.path.expanduser(config.SAVE_FILE)))
    repo_name = utils.get_repo_name()
    try:
        return data['%s:%s' % (repo_name, branchname)]
    except KeyError:
        # possibly one of the old ones
        return data[branchname]


def run():
    branchname = utils.get_current_branchname()
    data = load(branchname)
    _status = utils.call(['git', 'status', '--porcelain'])
    changed = [x for x in _status.splitlines() if not x.startswith('?? ')]
    if changed:
        print "ERROR. Some still changed files"
        print "\t", "\n\t".join(changed)
        exit()

    if data.get('gitflow'):
        print utils.call(['git', 'flow', 'feature', 'finish', branchname.replace('feature/', '')])
    else:
        print utils.call("git checkout master".split())
        print utils.call(['git', 'merge', branchname])
        print utils.call(['git', 'branch', '-d', branchname])

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
        print utils.call(cmd)
