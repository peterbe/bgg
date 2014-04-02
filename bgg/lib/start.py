import re
import datetime
import os
import json
import subprocess
import urllib
import urllib2
import getpass
import cookielib

from . import config
from . import utils


def get_bugzilla_summary(bugnumber):
    credentials = config.BUGZILLA_CREDENTIALS
    if not credentials:
        credentials = None
        bugzilla_login = raw_input('Bugzilla username: ')
        if bugzilla_login:
            bugzilla_password = getpass.getpass('Bugzilla password: ').strip()
            if bugzilla_password:
                login_payload = {
                    'Bugzilla_login': bugzilla_login,
                    'Bugzilla_password': bugzilla_password,
                    'Bugzilla_remember': 'on',
                    'GoAheadAndLogIn': 'Log in'
                }
                data = urllib.urlencode(login_payload)
                cookies = cookielib.LWPCookieJar()
                handlers = [
                    urllib2.HTTPHandler(),
                    urllib2.HTTPSHandler(),
                    urllib2.HTTPCookieProcessor(cookies)
                ]
                opener = urllib2.build_opener(*handlers)
                req = urllib2.Request(config.BUGZILLA_LOGIN_URL, data)
                response = opener.open(req)
                credentials = {'username': bugzilla_login}
                for cookie in cookies:
                    credentials[cookie.name] = cookie.value
                config.save_bugzilla_credentials(credentials)
                print "Your bugzilla cookie is now stored in",
                print config.CONFIG_FILE

    headers = {'Accept': 'application/json'}
    url = 'https://api-dev.bugzilla.mozilla.org/latest/bug/%s' % bugnumber
    request_arguments = {}
    if credentials:
        request_arguments['userid'] = credentials['Bugzilla_login']
        request_arguments['cookie'] = credentials['Bugzilla_logincookie']

    data = urllib.urlencode(request_arguments)
    if data:
        url += '?%s' % data
    req = urllib2.Request(url, headers=headers)
    try:
        response = urllib2.urlopen(req)
    except urllib2.URLError:
        import logging
        logging.error('Failed to connect to Bugzilla', exc_info=True)
        return ''
    assert response.code == 200, '%s - %s' % (response.code, response.read())
    the_page = response.read()
    struct = json.loads(the_page)
    return struct['summary']


def get_repo_name():
    # `git rev-parse --show-toplevel`
    d = call('git rev-parse --show-toplevel'.split())
    return os.path.split(d)[-1].strip()


def save(description, branchname, bugnumber, gitflow=False):
    try:
        data = json.load(open(os.path.expanduser(config.SAVE_FILE)))
    except IOError:
        data = {}
    repo_name = get_repo_name()
    data['%s:%s' % (repo_name, branchname)] = {
        'description': description,
        'bugnumber': bugnumber,
        'gitflow': gitflow,
        'date': datetime.datetime.now().isoformat()
    }
    json.dump(data, open(os.path.expanduser(config.SAVE_FILE), 'w'), indent=2)


def call(seq):
    """Use Popen to execute `seq` and return stdout."""
    return subprocess.Popen(seq,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT).communicate()[0]


def run(bugnumber=None):
    branches = utils.get_branches()
    if 'Not a git repository' in branches:
        print "Are you sure you're in a git repository?"
        return 1

    current_branchname = utils.get_current_branchname()
    print "You're currently on branch", current_branchname
    if bugnumber:
        summary = get_bugzilla_summary(bugnumber)
        summary = re.sub('^\[[\w-]+\]\s*', '', summary)
    else:
        summary = None
    if summary:
        description = raw_input('Summary ["%s"]: ' % summary).strip()
        if not description:
            description = summary
    else:
        description = raw_input("Summary: ").strip()

    branchname = ''
    if bugnumber:
        branchname = 'bug-%s-' % bugnumber

    def clean_branchname(string):
        string = (
            string
            .replace('   ', ' ')
            .replace('  ', ' ')
            .replace(' ', '-')
            .replace('=', '-')
            .replace('->', '-')
            .replace('---', '-')
        )
        for each in ':\'"/(),[].?`$<>':
            string = string.replace(each, '')
        return string.lower().strip()

    branchname += clean_branchname(description)
    if current_branchname == 'develop':
        print "(assuming this is a git flow repo)"
        print call(['git', 'flow', 'feature', 'start', branchname])
        branchname = 'feature/%s' % branchname
    else:
        print call(['git', 'checkout', '-b', branchname])
    save(description, branchname, bugnumber,
         gitflow=current_branchname == 'develop')
