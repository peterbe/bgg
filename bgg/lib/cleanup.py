import os
import json
import operator

from . import config
from . import utils
from . import merge
from . import branches


def run(search):
    if not search:
        print (
            "ERROR. You must supply a search term or "
            "the magically keyword MERGED"
        )
        exit()

    if search == 'MERGED':
        branches_ = branches.find(None)
        merged = branches.get_merged_branches()
        branches_ = [
            x for x in branches_
            if x['name'] in merged and x['name'] != 'master'
        ]
    else:
        branches_ = branches.find(search)
    branches_ = sorted(branches_, key=operator.itemgetter('dt'))
    if not branches_:
        print "ERROR. No branch matched by search"
        exit()
    elif len(branches_) > 1:
        if search == 'MERGED':
            branches.print_list(branches_, merged)
        elif search in [x['name'] for x in branches_]:
            # one of them was an exact match
            branches_ = [x for x in branches_ if x['name'] == search]
        else:
            # multiple and no exact match
            branches.print_list(
                branches_,
                branches.get_merged_branches()
            )
            print "ERROR. More than one match"
            exit()

    if search == 'MERGED':
        for branch in branches_:
            _cleanup(branch)
    else:
        _cleanup(branches_[0])

def _cleanup(branch):
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
        # branch_delete = raw_input(
        #     "Delete merged branch '%s'? [Y/n]" % branchname
        # ).lower().strip()
        if 1: #branch_delete not in ('n', 'no'):
            print utils.call(['git', 'branch', '-d', branchname])
            # remote_delete = raw_input(
            #     "Delete remote fork branch too? [Y/n]"
            # ).lower().strip()
            if 1: #remote_delete not in ('n', 'no'):
                print utils.call(
                    ['git', 'push', config.FORK_REMOTE_NAME, ':%s' % branchname]
                )
    else:
        print "%s can't be deleted because it's not merged" % _merged

    if return_to:
        print utils.call(['git', 'checkout', return_to])
