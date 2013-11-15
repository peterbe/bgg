import json
import os

CONFIG_FILE = os.path.expanduser('~/.G.json')


def write(data):
    with open(CONFIG_FILE, 'w') as out:
        json.dump(data, out, indent=2)


def read():
    with open(CONFIG_FILE) as inp:
        return json.load(inp)


if not os.path.isfile(CONFIG_FILE):
    # make a default one
    write({
        'SAVE_FILE': '~/.Gstart.json',
        'BUGZILLA_LOGIN_URL': 'https://bugzilla.mozilla.org/index.cgi',
        'FORK_REMOTE_NAME': 'myforkname'
    })

config = read()
SAVE_FILE = config['SAVE_FILE']
BUGZILLA_CREDENTIALS = config.get('BUGZILLA_CREDENTIALS', {})
BUGZILLA_LOGIN_URL = config['BUGZILLA_LOGIN_URL']
FORK_REMOTE_NAME = config['FORK_REMOTE_NAME']


def save_bugzilla_credentials(credentials):
    config = read()
    config['BUGZILLA_CREDENTIALS'] = credentials
    write(config)
