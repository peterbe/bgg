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
    parser.add_argument("start", nargs='?',
                        help="Start a new branch")
    parser.add_argument("branches", nargs='?',
                        help="List and search active branches")
    parser.add_argument("commit", nargs='?',
                        help="Commit the current branch")
    parser.add_argument("rebase", nargs='?',
                        help="Pull latest master and rebase against that")
    parser.add_argument("merge", nargs='?',
                        help="Merge the current branch onto master")
    parser.add_argument("makediff", nargs='?',
                        help="Make a diff file")
    parser.add_argument("--no-verify",
                        help="Makes sense if you use check.py",
                        action="store_true")
    args = parser.parse_args()
    print args
    if args.branches or args.start == 'branches':
        branches_ = branches.find(args.branches)
        if branches_:
            print "Found existing branches..."
            branches.print_list(branches_)
            if len(branches_) == 1:
                branch_name = branches_[0]['name']
                if len(branch_name) > 50:
                    branch_name = branch_name[:47] + '...'
                check_it_out = raw_input(
                    "Check out '%s'? [Y/n] " % branch_name
                )
                if check_it_out.lower().strip() != 'n':
                    branches.checkout(branches_[0]['name'])
        elif args.branches:
            print "Found no branches matching: %s" % args.branches
        else:
            print "Found no branches"
    elif args.commit or args.start == 'commit':
        if args.no_verify:
            commit.commit_all('--no-verify')
        else:
            commit.commit_all()
    elif args.merge or args.start == 'merge':
        merge.run()
    elif args.rebase or args.start == 'rebase':
        rebase.run()
    elif args.makediff or args.start == 'makediff':
        makediff.run()
    elif args.start == 'help':
        parser.print_help()
    elif not args.start.isdigit():
        parser.print_help()
    else:
        # start!
        start.run(args.start)
    return

    other_args = []
    if '--no-verify' in args:
        args.remove('--no-verify')
        other_args.append('--no-verify')

    if not args:
        # first, are we even in a git repository?

        # if there are staged or un-staged files,
        # you might want to do a commit
        files_staged_or_not_staged = state.files_staged_or_not_staged()
        if files_staged_or_not_staged:
            state.print_status()
            response = raw_input("\n\tWanna git commit all files? [Y/n]")
            if response.lower().strip() != 'n':
                current_branch = state.current_branch()
                if current_branch in ('master', 'develop'):
                    response = raw_input(
                        "You're currently on `%s`. Are you sure you want "
                        "commit from here? [y/N]"
                    )
                    if response.lower().strip() == 'y':
                        return commit.commit_all(*other_args)
                    else:
                        response = raw_input(
                            "\n\tWanna make a new branch? [Y/n]"
                        )
                        if response.lower().strip() != 'n':
                            start.run()
                        else:
                            print "\n\tThen you know what you're doing"
                else:
                    return commit.commit_all(*other_args)
                return
        else:
            # start a new branch
            start.run()
        return

    if len(args) == 1:
        if args[0].isdigit():
            # a bugnumber, either find an existing branch or create new one
            branches_ = branches.find(args[0])
            if branches_:
                print "Found existing branches..."
                for i, b in enumerate(branches_):
                    print "%d)  %s" % (i + 1, b['name'])
                print "0)  Create a new branch"
                number = raw_input('Select [0-%d]: ' % (i + 1))
                if number == '0':
                    start.run(args[0])
                else:
                    branch = branches_[int(number) - 1]
                    branches.checkout(branch['name'])
            else:
                start.run(args[0])
            return
        else:
            # a branch search
            branches_ = branches.find(args[0])
            print "Found existing branches..."
            branches.print_list(branches_)
            if len(branches_) == 1:
                branch_name = branches_[0]['name']
                if len(branch_name) > 50:
                    branch_name = branch_name[:47] + '...'
                check_it_out = raw_input("Check out '%s'? [Y/n]" % branch_name)
                if check_it_out.lower().strip() != 'n':
                    branches.checkout(branches_[0]['name'])
            return

    raise NotImplementedError(args)


if __name__ == '__main__':
    sys.exit(run())
