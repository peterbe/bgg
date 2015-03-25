import os
import json
import operator

from . import config
from . import utils
from . import merge
from . import branches


def run(search):
    if not search:
        print "ERROR. You must supply a search term"
        exit()

    branches_ = branches.find(search)
    branches_ = sorted(branches_, key=operator.itemgetter('dt'))
    if not branches_:
        print "ERROR. No branch matched by search"
        exit()
    elif len(branches_) > 1:
        branches.print_list(branches_)
        print "ERROR. More than one match"
        exit()

    branch = branches_[0]
    data = merge.load(branch['name'])

    current = utils.get_current_branchname()
    return_to = None
    if (
        (data.get('gitflow') and current != 'develop') or
        (not data.get('gitflow') and current != 'master')
    ):
        return_to = current
        if data.get('gitflow'):
            print utils.call('git checkout develop')
        else:
            print utils.call('git checkout master')

    if data.get('gitflow'):
        print utils.call('git pull origin develop')
    else:
        print utils.call('git pull origin master')

    _merged = [
        x.strip() for x in
        utils.call('git branch --merged').splitlines()
        if x.strip() and not x.strip().startswith('*')
    ]
    branchname = branch['name']
    if branchname in _merged:
        branch_delete = raw_input(
            "Delete merged branch '%s'? [Y/n]" % branchname
        ).lower().strip()
        if branch_delete not in ('n', 'no'):
            print utils.call(['git', 'branch', '-d', branchname])
            remote_delete = raw_input(
                "Delete remote fork branch too? [Y/n]"
            ).lower().strip()
            if remote_delete not in ('n', 'no'):
                print utils.call(
                    ['git', 'push', config.FORK_REMOTE_NAME, ':%s' % branchname]
                )
    else:
        print "%s can't be deleted because it's not merged" % _merged

    if return_to:
        print utils.call(['git', 'checkout', return_to])
