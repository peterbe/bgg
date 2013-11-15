import sys
from . import start
from . import branches
from . import state
from . import commit


def run():
    try:
        r = _run(sys.argv[1:])
    except KeyboardInterrupt:
        r = 0
        print
    return int(r or 0)

def _run(args):
    other_args = []
    if '--no-verify' in args:
        args.remove('--no-verify')
        other_args.append('--no-verify')

    if not args:
        # if there are staged or un-staged files,
        # you might want to do a commit
        files_staged_or_not_staged = state.files_staged_or_not_staged()
        if files_staged_or_not_staged:
            state.print_status()
            response = raw_input("\n\tWanna git commit all files? [Y/n]")
            if response.lower().strip() != 'n':
                current_branch = state.current_branch()
                if current_branch in ('master', 'develop'):
                    response = raw_input("You're currently on `%s`. Are you sure you want commit from here? [y/N]")
                    if response.lower().strip() == 'y':
                        return commit.commit_all(*other_args)
                    else:
                        response = raw_input("\n\tWanna make a new branch? [Y/n]")
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
    from bgg.main import run
    sys.exit(run())
