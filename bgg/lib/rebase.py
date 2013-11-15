import os
import json

from . import config
from . import utils


def get_repo_name():
    # `git rev-parse --show-toplevel`
    d = utils.call('git rev-parse --show-toplevel'.split())
    return os.path.split(d)[-1].strip()


def load(branchname):
    data = json.load(open(os.path.expanduser(config.SAVE_FILE)))
    repo_name = get_repo_name()
    try:
        return data['%s:%s' % (repo_name, branchname)]
    except KeyError:
        # possibly one of the old ones
        return data[branchname]


def run():
    branchname = utils.get_current_branchname()
    data = load(branchname)

    if data.get('gitflow'):
        print utils.call("git checkout develop".split())
        print utils.call("git pull origin develop".split())
        print utils.call(['git', 'checkout', branchname])
        #print utils.call("git flow feature rebase -i".split())
        print "Now run:\n"
        print "    ", "git flow feature rebase -i"
    else:
        print utils.call("git checkout master".split())
        print utils.call("git pull origin master".split())
        print utils.call(['git', 'checkout', branchname])
        #print utils.call("git rebase -i master".split())
        print "Now run:\n"
        print "    ", "git rebase -i master"
    print
