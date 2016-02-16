import re

from . import config
from . import utils


def run():
    branchname = utils.get_current_branchname()
    if branchname != 'master':
        print "Switching to the master branch"
        out, err = utils.call_and_error([
            'git', 'checkout', 'master'
        ])
        print out
        print err
    out, err = utils.call_and_error(
        "git fetch %s" % (config.FORK_REMOTE_NAME,)
    )
    out, err = utils.call_and_error(
        "git for-each-ref --sort=taggerdate "
        "--format %(refname) refs/tags".split()
    )
    latest_tag = out.strip().splitlines()[-1].replace('refs/tags/', '')
    print "Last tag was:", latest_tag

    new_tag = re.sub(
        '(\d+)(?!\d)',
        lambda x: str(int(x.group(0)) + 1),
        latest_tag
    )
    new_tag_input = raw_input("New tag ['%s']: " % new_tag).strip()
    new_tag = new_tag_input or new_tag
    # print "You want to create a new tag:", new_tag

    default_msg = 'Release %s' % new_tag
    msg = raw_input("Commit message ['%s']: " % default_msg)
    msg = msg or default_msg

    out, err = utils.call_and_error([
        'git', 'tag', '-a', new_tag,
        '-m', msg
    ])
    print out
    print err

    out, err = utils.call_and_error([
        'git', 'push', '--tags',
    ])
    print out
    print err
