import subprocess


def call(seq):
    if isinstance(seq, basestring):
        seq = seq.split()
    return subprocess.Popen(seq,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT).communicate()[0]


def _files():
    output = call('git status --porcelain')
    staged = []
    not_staged = []
    untracked = []
    for line in output.splitlines():
        info, path = line.split(' ', 1)
        if info.startswith('??'):
            untracked.append(path)
        elif info.startswith(' '):
            staged.append(path)
        else:
            not_staged.append(path)
    return staged, not_staged, untracked


def files_staged_or_not_staged():
    #output = call('git status --porcelain')
    staged, not_staged, untracked = _files()
    return staged + not_staged


def print_status():
    print call('git status')


def current_branch():
    output = call('git branch')
    for line in output.splitlines():
        if line.startswith('* '):
            return line[2:]
