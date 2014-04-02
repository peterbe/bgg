import os
import re
import stat
import datetime
import json

from . import config
from . import utils


def save(description, branchname, bugnumber):
    data = json.load(open(os.path.expanduser(config.SAVE_FILE)))
    if branchname in data:
        # old style
        key = branchname
    else:
        key = '%s:%s' % (utils.get_repo_name(), branchname)
    data[key] = {'description': description, 'bugnumber': bugnumber}
    json.dump(open(os.path.expanduser(config.SAVE_FILE), 'w'), indent=2)


def load(branchname):
    data = json.load(open(os.path.expanduser(config.SAVE_FILE)))
    try:
        return data['%s:%s' % (utils.get_repo_name(), branchname)]
    except KeyError:
        return data[branchname]


def _find_git_root(dir_):
    dir_ = os.path.normpath(dir_)
    if dir_ == '/':
        raise OSError("Can't find .git/ parent")
    if os.path.isdir(os.path.join(dir_, '.git')):
        return dir_
    return _find_git_root(os.path.join(dir_, '..'))


def commit_all(*args):
    #branches = utils.call(['git', 'branch'])[0]
    #branchname = [
    #    x.replace('* ', '').strip()
    #    for x in branches.splitlines()
    #    if x.startswith('* ')
    #][0]
    branchname = utils.get_current_branchname()
    data = load(branchname)

    _status = utils.call(['git', 'status', '--porcelain'])
    unstaged = [
        x.replace('?? ', '').strip()
        for x in _status.splitlines()
        if x.startswith('?? ')
    ]
    if unstaged:
        print "NOTE! There are untracked files:"
        _root = _find_git_root(os.curdir)
        _now = datetime.datetime.now()
        _youngest_new_file = None
        for each in unstaged:
            filepath = os.path.join(_root, each)
            try:
                ts = os.stat(filepath)[stat.ST_MTIME]
                mod_time = datetime.datetime.fromtimestamp(ts)
                print ' ' * 4,
                print filepath.replace(_root, '').ljust(60),
                _age = _now - mod_time
                if _youngest_new_file is None:
                    _youngest_new_file = _age
                elif _age < _youngest_new_file:
                    _youngest_new_file = _age
                age = str(_age)
                if ' days,' in age:
                    age = re.findall('\d+ days', age)[0]
                else:
                    age = re.sub(':(\d\d)\.\d+', r':\1', age)
            except OSError:
                age = 'n/a'
            print age

        if _youngest_new_file and _youngest_new_file.total_seconds() < 60 * 60 * 12:
            # if a file has been added in the last 12 hours, we have to ask
            # this question
            ignore = raw_input("Ignore untracked files? [Y/n]").lower().strip()
            if ignore.lower().strip() == 'n':
                print (
                    "\n\tLeaving it to you to figure out what to do with "
                    "the untracked files"
                )
                return 1
            print

    if data['bugnumber']:
        msg = 'bug %s - %s' % (data['bugnumber'], data['description'])
    else:
        msg = data['description']

    print "MSG:"
    print "\t", msg
    print
    confirm = raw_input("OK? [Y/n] ").lower().strip()
    if confirm in ('n', 'no'):
        try_again = raw_input("Type your own (or empty to exit): ")
        if not try_again:
            return 1
        msg = try_again

    if data['bugnumber']:
        fixes_prefix = raw_input(
            "Add the 'fixes ' prefix? [N/y] "
        ).lower().strip()
        if fixes_prefix in ('y', 'yes'):
            msg = 'fixes %s' % msg

    cmd = ['git', 'commit', '-a', '-m', msg]
    #cmd = ['git', 'commit', '-m', msg]
    if '--no-verify' in args:
        cmd.append('--no-verify')
    out, err = utils.call_and_error(cmd)
    if err and err.strip():
        print err
        return 1
    print "NOW, feel free to run:\n"
    print "git checkout master"
    print "git merge %s" % branchname
    print "git branch -d %s" % branchname
    print
    print "OR\n"
    print "git push %s %s" % (config.FORK_REMOTE_NAME, branchname)
    print
    push_for_you = raw_input("Run that push? [Y/n] ").lower().strip()
    if push_for_you not in ('n', 'no'):
        cmd = ['git', 'push', config.FORK_REMOTE_NAME, branchname]
        out, err = utils.call_and_error(cmd)
        if err and err.strip():
            print err
            return 2

    return 0
