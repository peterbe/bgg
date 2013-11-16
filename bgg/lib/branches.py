import operator
import subprocess
import datetime
from email.utils import parsedate_tz

def call(seq):
    if isinstance(seq, basestring):
        seq = seq.split()
    return subprocess.Popen(seq,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT).communicate()[0]


def _parse_branch_info(output):
    info = {}
    commit_msg = None
    for thing in output.splitlines():
        if commit_msg is not None:
            commit_msg += thing + '\n'
            continue
        if thing.startswith('commit'):
            continue
        if thing == '':
            commit_msg = ''
            continue
        label, stuff = thing.split(':', 1)
        info[label.strip()] = stuff.strip()

    info['msg'] = commit_msg
    return info


def branch_info(name):
    output = call('git log -n 1 %s' % name)
    info = _parse_branch_info(output)

    info['name'] = name
    info['date'] = info['Date']
    info['dt'] = parsedate_tz(info['date'])
    info['dt'] = datetime.datetime(*info['dt'][:7])
    age = datetime.datetime.now() - info['dt']

    info['age'] = age
    return info


def find(search):
    refs = call('git for-each-ref --shell refs/')
    branches = []
    for ref in refs.splitlines():
        try:
            branch_name = ref.split('refs/heads/')[1][:-1]
        except IndexError:
            continue
        if search and search.lower() not in branch_name.lower():
            continue
        branches.append(branch_info(branch_name))
    return branches


def checkout(branch_name):
    call('git checkout %s' % branch_name)


def print_list(branches):
    for each in sorted(branches, key=operator.itemgetter('dt')):
        print '-' * 79
        print each['name']
        print "\t", each['date']
        print "\t", each['age'], "ago"
        print "\t", each['msg'].strip()
        print


def run(searchstring):
    branches_ = find(searchstring)
    if branches_:
        print "Found existing branches..."
        print_list(branches_)
        if len(branches_) == 1:
            branch_name = branches_[0]['name']
            if len(branch_name) > 50:
                branch_name = branch_name[:47] + '...'
            check_it_out = raw_input(
                "Check out '%s'? [Y/n] " % branch_name
            )
            if check_it_out.lower().strip() != 'n':
                checkout(branches_[0]['name'])
    elif searchstring:
        print "Found no branches matching: %s" % searchstring
    else:
        print "Found no branches"
