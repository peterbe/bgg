import os
import json

from . import config
from . import utils
from . import merge


def run():
    branchname = utils.get_current_branchname()
    if branchname == 'master':
        print "ERROR. You're already on the master branch."
        exit()
    data = merge.load(branchname)
    _status = utils.call(['git', 'status', '--porcelain'])
    changed = [x for x in _status.splitlines() if not x.startswith('?? ')]
    if changed:
        print "ERROR. Some still changed files"
        print "\t", "\n\t".join(changed)
        exit()
    if data.get('gitflow'):
        print utils.call('git checkout develop')
        print utils.call('git pull origin develop')
    else:
        print utils.call('git checkout master')
        print utils.call('git pull origin master')
    _merged = [
        x.strip() for x in
        utils.call('git branch --merged').splitlines()
        if x.strip() and not x.strip().startswith('*')
    ]
    if branchname in _merged:
        branch_delete = raw_input(
            "Delete merged branch '%s'? [Y/n]" % branchname
        ).lower().strip()
        if branch_delete not in ('n', 'no'):
            # print ' '.join(['git', 'branch', '-d', branchname])
            print utils.call(['git', 'branch', '-d', branchname])
            remote_delete = raw_input(
                "Delete remote fork branch too? [Y/n]"
            ).lower().strip()
            if remote_delete not in ('n', 'no'):
                print utils.call(
                    ['git', 'push', config.FORK_REMOTE_NAME, ':%s' % branchname]
                )
                # print ' '.join(['git', 'push', config.FORK_REMOTE_NAME, ':%s' % branchname])
