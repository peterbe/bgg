import os
import json

from . import config
from . import utils

from .merge import load


def run(force=False):
    branchname = utils.get_current_branchname()
    data = load(branchname)

    if force:
        if branchname == 'master' or config.FORK_REMOTE_NAME == 'origin':
            print "ERROR! I don't dare force push to that!"
            return 1

    cmd = ['git', 'push']
    if force:
        cmd.append('--force')
    cmd += [config.FORK_REMOTE_NAME, branchname]

    out, err = utils.call_and_error(cmd)
    print out
    print err

    return 0
