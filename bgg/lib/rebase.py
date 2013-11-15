import os
import json
import subprocess


from . import config


def get_repo_name():
    # `git rev-parse --show-toplevel`
    d = call('git rev-parse --show-toplevel'.split())
    return os.path.split(d)[-1].strip()


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

    if data.get('gitflow'):
        print call("git checkout develop".split())
        print call("git pull origin develop".split())
        print call(['git', 'checkout', branchname])
        #print call("git flow feature rebase -i".split())
        print "Now run:\n"
        print "    ", "git flow feature rebase -i"
    else:
        print call("git checkout master".split())
        print call("git pull origin master".split())
        print call(['git', 'checkout', branchname])
        #print call("git rebase -i master".split())
        print "Now run:\n"
        print "    ", "git rebase -i master"
    print
