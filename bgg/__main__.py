import sys
from lib import start
from lib import branches
from lib import state
from lib import commit
from lib import merge
from lib import rebase
from lib import makediff


def run():
    try:
        r = _run()
    except KeyboardInterrupt:
        r = 0
        print
    return int(r or 0)


def _run():
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    ##
    ## Branches
    ##

    def run_branches(args):
        branches.run(args.searchstring)

    p = subparsers.add_parser(
        'branches',
        help="List and search active branches"
    )
    p.set_defaults(func=run_branches)
    p.add_argument('searchstring', nargs='?', help='Branch search string')

    ##
    ## Start
    ##
    def run_start(args):
        if args.bugid and not args.bugid.isdigit():
            print >>sys.stderr, "Bug ID not a number"
            #parser.print_help()
        else:
            start.run(args.bugid)

    p = subparsers.add_parser('start', help="Start a new branch")
    p.set_defaults(func=run_start)
    p.add_argument('bugid', nargs='?', help='Optional Bugzilla ID')

    ##
    ## Commit
    ##
    def run_commit(args):
        if args.no_verify:
            commit.commit_all('--no-verify')
        else:
            commit.commit_all()

    p = subparsers.add_parser('commit', help="Commit the current branch")
    p.set_defaults(func=run_commit)
    p.add_argument("--no-verify",
                   help="Makes sense if you use check.py",
                   action="store_true")

    ##
    ## Rebase
    ##
    def run_rebase(args):
        rebase.run()

    p = subparsers.add_parser('rebase', help="Pull latest master and rebase against that")
    p.set_defaults(func=run_rebase)

    ##
    ## Merge
    ##
    def run_merge(args):
        merge.run()

    p = subparsers.add_parser('merge', help="Merge the current branch onto master")
    p.set_defaults(func=run_merge)

    ##
    ## Makediff
    ##
    def run_makediff(args):
        makediff.run()

    p = subparsers.add_parser('makediff', help="Make a diff file")
    p.set_defaults(func=run_makediff)

    ##
    ##
    ##

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    sys.exit(run())
